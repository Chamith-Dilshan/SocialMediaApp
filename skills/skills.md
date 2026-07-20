For a clean architecture, services should call other services when you're invoking business logic, not repositories
directly.

Good
PostLikeService
-> PostService.verify_post_exists()

FollowService
-> UserService.get_user()

Because:

Business rules stay in one place.
Validation stays in one place.
Future changes affect only one service.
Bad
PostLikeService
-> PostRepository

CommentService
-> PostRepository

BookmarkService
-> PostRepository

A common rule:

Call Service when

You need business logic.

Call Repository when

You only need data access.

Repository
returns ORM Models

Service
applies business rules
converts ORM -> DTO

Router
returns DTO