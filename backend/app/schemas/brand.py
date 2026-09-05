from pydantic import BaseModel, ConfigDict, Field


class BrandCreate(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=100,
    )

    slug: str = Field(
        min_length=2,
        max_length=120,
        pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
    )


class BrandUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    slug: str | None = Field(
        default=None,
        min_length=2,
        max_length=120,
        pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
    )

    is_active: bool | None = None


class BrandResponse(BaseModel):
    id: int
    name: str
    slug: str
    is_active: bool

    model_config = ConfigDict(
        from_attributes=True
    )


class BrandListResponse(BaseModel):
    items: list[BrandResponse]
    page: int
    page_size: int
    total: int