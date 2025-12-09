from datetime import datetime, timezone
from typing import List, Optional, Dict, Set
from fastapi.requests import Request

from httpx import HTTPStatusError

from microfastapitodowebapp.config.jinja import templates
from microfastapitodowebapp.model.todo_form_data import TodoFormData
from microfastapitodowebapp.model.todo_request import (
    TodoCreateRequest,
    TodoPatchRequest,
    TodoPatchNoDateRequest,
    TodoShareRequest,
)
from microfastapitodowebapp.service import share as share_service


def normalize_list(value: Optional[List[str]] | Optional[List[int]]) -> list:
    return value or []


def parse_deadline(deadline_date: str | None, deadline_time: str | None) -> datetime | None:
    if not deadline_date or not deadline_date.strip():
        return None

    t_str = (deadline_time or "").strip() or "00:00"

    if len(t_str) == 5:
        t_str += ":00"

    try:
        dt = datetime.strptime(f"{deadline_date}T{t_str}", "%Y-%m-%dT%H:%M:%S")
        return dt.replace(tzinfo=timezone.utc)
    except ValueError as e:
        print(f"Date parsing error: {e}")
        return None


def build_create_request(form_data: TodoFormData) -> TodoCreateRequest:
    deadline_dt = parse_deadline(form_data.deadline_date, form_data.deadline_time)
    categories = normalize_list(form_data.categories)

    return TodoCreateRequest(
        title=form_data.title,
        description=form_data.description,
        priority=form_data.priority,
        completed=form_data.completed,
        deadline=deadline_dt,
        categories=categories,
    )


def build_patch_request(form_data: TodoFormData) -> TodoPatchRequest | TodoPatchNoDateRequest:
    categories = normalize_list(form_data.categories)
    current_utc = datetime.now(timezone.utc)
    deadline_dt = parse_deadline(form_data.deadline_date, form_data.deadline_time)

    if deadline_dt and deadline_dt < current_utc:
        return TodoPatchNoDateRequest(
            title=form_data.title,
            description=form_data.description,
            priority=form_data.priority,
            completed=form_data.completed,
            categories=categories,
        )

    return TodoPatchRequest(
        title=form_data.title,
        description=form_data.description,
        priority=form_data.priority,
        completed=form_data.completed,
        deadline=deadline_dt,
        categories=categories,
    )


async def create_shares_from_form(request: Request,
                                  todo_id: int,
                                  shares_email: Optional[List[str]],
                                  shares_access_level: Optional[List[int]],
                                  *,
                                  skip_first: bool = False, ) -> bool:
    emails = normalize_list(shares_email)
    levels = normalize_list(shares_access_level)

    if skip_first:
        emails = emails[1:]
        levels = levels[1:]

    if not emails or not levels:
        return True

    all_success = True

    for email, level in zip(emails, levels):
        clean_email = (email or "").strip()
        if not clean_email:
            continue

        try:
            share_req = TodoShareRequest(email=clean_email, accessLevel=level)
            await share_service.create_todo_share(request, todo_id, share_req)
        except HTTPStatusError as e:
            print(f"Failed to share with {clean_email}: {e.response.text}")
            all_success = False
        except Exception as e:
            print(f"Failed to share with {clean_email}: {e}")
            all_success = False

    return all_success


async def sync_shares_from_form(request: Request,
                                todo_id: int,
                                shares_email: Optional[List[str]],
                                shares_access_level: Optional[List[int]],
                                *,
                                skip_first: bool = True, ) -> bool:
    errors_occurred = False

    try:
        emails = normalize_list(shares_email)
        levels = normalize_list(shares_access_level)

        if skip_first:
            emails = emails[1:]
            levels = levels[1:]

        target_shares_map: Dict[str, int] = {}
        for email, level in zip(emails, levels):
            clean_email = (email or "").strip()
            if clean_email:
                target_shares_map[clean_email] = level

        current_shares_response = await share_service.get_todo_shares(request, todo_id)
        current_shares_map: Dict[str, int] = {
            s.email: s.access_level for s in current_shares_response.content if s.access_level != 3
        }

        target_keys: Set[str] = set(target_shares_map.keys())
        current_keys: Set[str] = set(current_shares_map.keys())

        emails_to_add = target_keys - current_keys
        emails_to_delete = current_keys - target_keys
        emails_to_check = target_keys.intersection(current_keys)

        for email in emails_to_delete:
            try:
                await share_service.delete_todo_share(request, todo_id, email)
            except Exception as e:
                print(f"Failed to delete share {email}: {e}")
                errors_occurred = True

        for email in emails_to_add:
            try:
                level = target_shares_map[email]
                share_req = TodoShareRequest(email=email, accessLevel=level)
                await share_service.create_todo_share(request, todo_id, share_req)
            except Exception as e:
                print(f"Failed to add share {email}: {e}")
                errors_occurred = True

        for email in emails_to_check:
            new_level = target_shares_map[email]
            old_level = current_shares_map[email]

            if new_level != old_level:
                try:
                    await share_service.delete_todo_share(request, todo_id, email)
                    share_req = TodoShareRequest(email=email, accessLevel=new_level)
                    await share_service.create_todo_share(request, todo_id, share_req)
                except Exception as e:
                    print(f"Failed to update share level for {email}: {e}")
                    errors_occurred = True

    except Exception as e:
        print(f"Critical error during share sync: {e}")
        errors_occurred = True

    return not errors_occurred


def create_toast_response(request: Request,
                          shares_ok: bool = True,
                          is_error: bool = False,
                          custom_message: str = None):
    if is_error:
        toast_type = "error"
        toast_msg = custom_message or "We couldn’t save your changes. Please try again."
    elif not shares_ok:
        toast_type = "warning"
        toast_msg = custom_message or "Saved, but sharing could not be completed."
    else:
        toast_type = "success"
        toast_msg = custom_message or "Your changes have been saved."

    return templates.TemplateResponse(
        request=request,
        name="dashboard/content.html",
        context={
            "toast_message": toast_msg,
            "toast_type": toast_type
        }
    )
