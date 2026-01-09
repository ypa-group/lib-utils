from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


__all__ = ("AppVersionCheckingMiddleware",)


class AppVersionCheckingMiddleware(BaseHTTPMiddleware):
    def __init__(
            self,
            app,
            microservice_client_path: str,
            app_android_minimal_version: str | None = None,
            app_android_current_version: str | None = None,
            app_ios_minimal_version: str | None = None,
            app_ios_current_version: str | None = None,
    ):
        super().__init__(app)
        self.microservice_client_path = microservice_client_path
        self.app_android_minimal_version = app_android_minimal_version
        self.app_android_current_version = app_android_current_version
        self.app_ios_minimal_version = app_ios_minimal_version
        self.app_ios_current_version = app_ios_current_version


    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        from_frontend = path.startswith(self.microservice_client_path) #DOCS_CONSTANTS.MICROSERVICE_BRANCH
        if from_frontend:
            if request.headers.get("x-android-app-version", None) is not None and self.app_android_minimal_version is not None:
                if tuple([int(x) for x in str(request.headers["x-android-app-version"]).split(".")]) < tuple([int(x) for x in self.app_android_minimal_version.split(".")]):
                    return Response(status_code=426, content="upgrade_required")
            elif request.headers.get("x-ios-app-version", None) is not None and self.app_ios_minimal_version is not None:
                if tuple([int(x) for x in str(request.headers["x-ios-app-version"]).split(".")]) < tuple([int(x) for x in self.app_ios_minimal_version.split(".")]):
                    return Response(status_code=426, content="upgrade_required")
        response = await call_next(request)
        if from_frontend:
            if request.headers.get("x-android-app-version", None) is not None and self.app_android_current_version is not None:
                if tuple([int(x) for x in str(request.headers["x-android-app-version"]).split(".")]) < tuple([int(x) for x in self.app_android_current_version.split(".")]):
                    response.headers["update_needed"] = self.app_android_current_version
            elif request.headers.get("x-ios-app-version", None) is not None and self.app_ios_current_version is not None:
                if tuple([int(x) for x in str(request.headers["x-ios-app-version"]).split(".")]) < tuple([int(x) for x in self.app_ios_current_version.split(".")]):
                    response.headers["update_needed"] = self.app_ios_current_version
        return response
