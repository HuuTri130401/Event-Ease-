import logging
import traceback
from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from app.core.security import check_permissions
from app.helpers.exception_handler import CustomException
from app.helpers.paging import Page, PaginationParams, paginate
from app.models.model_user import User
from app.schemas.base import DataResponse
from app.schemas.user import (
    UserItemResponse,
    UserRegisterRequest,
    UserRequestUpdate,
)
from app.schemas.user_role import UserWithRolesResponse
from app.services.user_service import UserService, get_user_service

logger = logging.getLogger()
router = APIRouter()


@router.get(
    "",
    response_model=Page[UserItemResponse],
    summary="Danh sách người dùng",
    dependencies=[Depends(check_permissions(["ADMIN"]))],
)  # API Get list User
def get(
    params: PaginationParams = Depends(),
    user_service: UserService = Depends(get_user_service),
) -> Any:
    try:
        _query = user_service.get_all_user()
        users = paginate(model=User, query=_query, params=params)
        return users
    except Exception as e:
        error_details = traceback.format_exc()  # Lấy traceback đầy đủ
        print(f"Error occurred: {error_details}")
        raise CustomException(
            http_code=400, code="400", message=f"{str(e)}: {error_details}"
        )


@router.get(
    "/{id}",
    response_model=DataResponse[UserItemResponse],
    summary="Thông tin chi tiết người dùng",
    dependencies=[Depends(check_permissions(["ADMIN"]))],
)
def get_detail(id: int, user_service: UserService = Depends(get_user_service)):
    try:
        data = user_service.get_user_by_id(id)
        return DataResponse().custom_response(
            code="200", message="Xem thông tin chi tiết người dùng", data=data
        )
    except CustomException as e:
        raise CustomException(http_code=400, code="400", message=str(e))


@router.get(
    "/{user_id}/roles",
    response_model=DataResponse[UserWithRolesResponse],
    summary="Lấy danh sách vai trò của người dùng",
)
def get_roles_of_user(
    user_id: int, user_service: UserService = Depends(get_user_service)
) -> Any:
    try:
        data = user_service.get_roles_by_user_id(user_id)
        return DataResponse().custom_response(
            code="200", message="Lấy danh sách vai trò của người dùng", data=data
        )
    except Exception as e:
        error_details = traceback.format_exc()  # Lấy traceback đầy đủ
        print(f"Error occurred: {error_details}")
        raise CustomException(
            http_code=400, code="400", message=f"{str(e)}: {error_details}"
        )


@router.put(
    "/{user_id}/roles/{role_id}",
    summary="Gỡ bỏ vai trò của người dùng",
    dependencies=[Depends(check_permissions(["ADMIN"]))],
)
def remove_role_from_user(
    user_id: int, role_id: int, user_service: UserService = Depends(get_user_service)
):
    try:
        result = user_service.remove_role_from_user(user_id=user_id, role_id=role_id)
        return DataResponse().custom_response(
            code="200", message="Vai trò đã được gỡ bỏ", data=result
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"Error occurred: {error_details}")
        raise CustomException(http_code=400, code="400", message=str(e))


@router.put(
    "/change_status/{user_id}",
    response_model=DataResponse[UserItemResponse],
    summary="Khóa / Mở khóa người dùng",
    dependencies=[Depends(check_permissions(["ADMIN"]))],
)
def change_status(user_id: int, user_service: UserService = Depends(get_user_service)):
    try:
        result = user_service.change_status(user_id=user_id)
        return DataResponse().custom_response(
            code="200", message="Chuyển đổi trạng thái thành công", data=result
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"Error occurred: {error_details}")
        raise CustomException(http_code=400, code="400", message=str(e))


@router.put(
    "/{id}",
    response_model=DataResponse[UserItemResponse],
    summary="Cập nhật người dùng",
)
def update_user(
    id: int,
    data: UserRequestUpdate,
    user_service: UserService = Depends(get_user_service),
) -> Any:
    try:
        user = user_service.update_user(id, data)
        return DataResponse().custom_response(
            code="200", message="Cập nhật người dùng thành công", data=user
        )
    except Exception as e:
        raise CustomException(http_code=400, code="400", message=str(e))


@router.delete(
    "/delete_user/{user_id}",
    summary="Xóa người dùng",
    dependencies=[Depends(check_permissions(["ADMIN"]))],
)
def delete_user(user_id: int, user_service: UserService = Depends(get_user_service)):
    try:
        result = user_service.delete_user(user_id=user_id)
        return DataResponse().custom_response(
            code="200", message=f"Xóa người dùng thành công", data=result
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"Error occurred: {error_details}")
        raise CustomException(http_code=400, code="400", message=str(e))


@router.post(
    "/register",
    response_model=DataResponse[UserItemResponse],
    summary="Tạo mới người dùng",
)
def create_user(
    user_data: UserRegisterRequest,
    user_service: UserService = Depends(get_user_service),
) -> Any:
    try:
        new_user = user_service.create_user(user_data)
        return DataResponse().custom_response(
            code="201", message="Tạo mới người dùng thành công", data=new_user
        )
    except Exception as e:
        raise CustomException(http_code=400, code="400", message=str(e))


@router.post(
    "/{user_id}/roles",
    response_model=None,
    summary="Gán vai trò cho người dùng",
    dependencies=[Depends(check_permissions(["ADMIN"]))],
)
def assign_roles_to_user(
    user_id: int,
    role_ids: list[int],
    user_service: UserService = Depends(get_user_service),
):
    try:
        data = user_service.assign_roles_to_user(user_id, role_ids)
        return DataResponse().custom_response(
            code="201", message="Gán vai trò cho người dùng thành công", data=data
        )
    except CustomException as e:
        raise CustomException(http_code=400, code="400", message=str(e))
