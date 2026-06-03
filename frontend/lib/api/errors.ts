type ValidationErrorItem = {
  msg?: string;
  loc?: Array<string | number>;
};

export function formatApiError(body: unknown, fallback = "Request failed."): string {
  if (!body || typeof body !== "object") {
    return fallback;
  }

  const detail = (body as { detail?: unknown }).detail;

  if (typeof detail === "string") {
    return detail;
  }

  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        if (typeof item === "string") {
          return item;
        }

        if (item && typeof item === "object") {
          const validationItem = item as ValidationErrorItem;
          const location = validationItem.loc?.filter((part) => part !== "body").join(".");
          const message = validationItem.msg ?? "Invalid value";

          return location ? `${location}: ${message}` : message;
        }

        return "Invalid request";
      })
      .join(" ");
  }

  return fallback;
}
