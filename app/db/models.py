from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    api_key = Column(String, unique=True, index=True)
    tweets = relationship("Tweet", back_populates="author")
    followers = relationship(
        "UserFollower",
        back_populates="follower",
        foreign_keys="UserFollower.follower_id",
    )
    following = relationship(
        "UserFollower",
        back_populates="following",
        foreign_keys="UserFollower.following_id",
    )
    media = relationship("Media", back_populates="uploader")

    def __repr__(self) -> str:
        """
        Возвращает строковое представление пользователя.

        Возвращаемое значение:
        - str: строковое представление пользователя в формате
        "<User(id={id}, name={name}, api_key={api_key})>"
        """
        return f"<User(id={self.id}, name={self.name}, api_key={self.api_key})>"


class Tweet(Base):
    __tablename__ = "tweets"
    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    author = relationship("User", back_populates="tweets")
    media_links = relationship("TweetMedia", back_populates="tweet")
    likes = relationship("TweetLike", back_populates="tweet")

    def __repr__(self) -> str:
        """
        Возвращает строковое представление твита.

        Возвращаемое значение:
        - str: строковое представление твита в формате
        "<Tweet(id={id}, content={content}, user_id={user_id})>"
        """
        return f"<Tweet(id={self.id}, content={self.content}, user_id={self.user_id})>"


class Media(Base):
    __tablename__ = "media"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    file_path = Column(String, index=True)

    uploader = relationship("User", back_populates="media")
    tweet_media = relationship("TweetMedia", back_populates="media")

    def __repr__(self) -> str:
        """
        Возвращает строковое представление медиа.

        Возвращаемое значение:
        - str: строковое представление медиа в формате
        "<Media(id={id}, file_path={file_path})>"
        """
        return f"<Media(id={self.id}, file_path={self.file_path})>"


class TweetLike(Base):
    __tablename__ = "tweet_likes"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    tweet_id = Column(Integer, ForeignKey("tweets.id"))
    user = relationship("User")
    tweet = relationship("Tweet", back_populates="likes")

    def __repr__(self) -> str:
        """
        Возвращает строковое представление лайка твита.

        Возвращаемое значение:
        - str: строковое представление лайка в формате
        "<TweetLike(id={id}, user_id={user_id}, tweet_id={tweet_id})>"
        """
        return (
            f"<TweetLike(id={self.id}, "
            f"user_id={self.user_id}, "
            f"tweet_id={self.tweet_id})>"
        )


class UserFollower(Base):
    __tablename__ = "user_followers"
    id = Column(Integer, primary_key=True, index=True)
    follower_id = Column(Integer, ForeignKey("users.id"))
    following_id = Column(Integer, ForeignKey("users.id"))
    follower = relationship(
        "User", foreign_keys=[follower_id], back_populates="followers"
    )
    following = relationship(
        "User", foreign_keys=[following_id], back_populates="following"
    )

    def __repr__(self) -> str:
        """
        Возвращает строковое представление подписки пользователя.

        Возвращаемое значение:
        - str: строковое представление подписки в формате "<UserFollower(id={id},
        follower_id={follower_id}, following_id={following_id})>"
        """
        return (
            f"<UserFollower(id={self.id}, "
            f"follower_id={self.follower_id}, "
            f"following_id={self.following_id})>"
        )


class TweetMedia(Base):
    __tablename__ = "tweet_media"
    id = Column(Integer, primary_key=True, index=True)
    tweet_id = Column(Integer, ForeignKey("tweets.id"))
    media_id = Column(Integer, ForeignKey("media.id"))
    tweet = relationship("Tweet", back_populates="media_links")
    media = relationship("Media", back_populates="tweet_media")

    def __repr__(self) -> str:
        """
        Возвращает строковое представление связи между твитом и медиа.

        Возвращаемое значение:
        - str: строковое представление связи между твитом и медиа в формате
        "<TweetMedia(id={id}, tweet_id={tweet_id}, media_id={media_id})>"
        """
        return (
            f"<TweetMedia(id={self.id},"
            f"tweet_id={self.tweet_id},"
            f"media_id={self.media_id})>"
        )
