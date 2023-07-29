#!/usr/bin/env python3
import datetime
import json

# import logging # @TODO: implement logging
import os
from dataclasses import dataclass
from enum import Enum
from typing import List, Any, Optional, Union

import requests
from requests import Response


def from_int(x: Any) -> int:
    assert isinstance(x, int) and not isinstance(x, bool)
    return x


def from_str(x: Any) -> str:
    # assert isinstance(x, str) # @TODO: fix this
    return x


def from_bool(x: Any) -> bool:
    # assert isinstance(x, bool)
    return x


def from_union(fs, x):
    for f in fs:
        try:
            return f(x)
        except BaseException:
            pass
    # assert False # @TODO: fix this


def from_list(f, x):
    assert isinstance(x, list)
    return [f(y) for y in x]


def from_dict(f, x):
    assert isinstance(x, dict)
    return f.from_dict(x)


def from_none(x):
    assert x is None
    return x


def to_str(x: str) -> str:
    # assert isinstance(x, str)
    return x


def to_enum(x: Any) -> Enum:
    # assert isinstance(x, c) # @TODO: fix this
    return x


def to_class(c, x: Any) -> Enum:
    assert isinstance(x, c)
    return x.to_dict()


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.value
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        if isinstance(obj, ItemType):
            return obj.value
        return json.JSONEncoder.default(self, obj)


class ItemType(Enum):
    LOGIN = 1
    SECURE_NOTE = 2
    CARD = 3
    IDENTITY = 4

    @staticmethod
    def to_dict(self):
        return self.value


class CardType(Enum):
    VISA = 1
    MASTERCARD = 2
    AMERICAN_EXPRESS = 3
    DISCOVER = 4
    JCB = 5
    DINERS_CLUB = 6
    UNKNOWN = 7

    @staticmethod
    def to_dict(self):
        return self.value


class MatchType(Enum):
    DOMAIN = 0
    HOST = 1
    STARTS_WITH = 2
    EXACT = 3
    REGULAR_EXPRESSION = 4
    NEVER = 5

    @staticmethod
    def to_dict(self):
        return self.value


class MemberType(Enum):
    Owner = 0
    Admin = 1
    User = 2
    Manager = 3
    Custom = 4

    @staticmethod
    def to_dict(self):
        return self.value


class SendType(Enum):
    TEXT = 0
    FILE = 1

    @staticmethod
    def to_dict(self):
        return self.value


@dataclass
class Uri:
    match: Optional[MatchType]
    uri: Optional[str]

    @staticmethod
    def from_dict(obj: Any) -> "Uri":
        assert isinstance(obj, dict)
        match = from_union([MatchType, from_none], obj.get("match"))
        uri = from_union([from_str, from_none], obj.get("uri"))
        return Uri(match, uri)

    def to_dict(self) -> dict:
        result: dict = {
            "match": from_union(
                [lambda x: to_enum(MatchType, x), from_none], self.match
            ),
            "uri": from_union([from_str, from_none], self.uri),
        }
        return result

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @staticmethod
    def from_json(s: str) -> "Uri":
        return Uri.from_dict(json.loads(s))

    def to_file(self, path: str) -> None:
        with open(path, "w") as f:
            f.write(self.to_json())

    @staticmethod
    def from_file(path: str) -> "Uri":
        return Uri.from_dict(json.loads(path))


@dataclass
class Login:
    uris: Optional[List[Uri]]
    username: Optional[str]
    password: Optional[str]
    totp: Optional[str]

    @staticmethod
    def from_dict(obj: Any) -> "Login":
        assert isinstance(obj, dict)
        uris = from_union(
            [lambda x: from_list(Uri.from_dict, x), from_none], obj.get("uris")
        )
        username = from_union([from_str, from_none], obj.get("username"))
        password = from_union([from_str, from_none], obj.get("password"))
        totp = from_union([from_str, from_none], obj.get("totp"))
        return Login(uris, username, password, totp)

    def to_dict(self) -> dict:
        result: dict = {
            "uris": from_union(
                [lambda x: from_list(lambda y: to_class(Uri, y), x), from_none],
                self.uris,
            ),
            "username": from_union([from_str, from_none], self.username),
            "password": from_union([from_str, from_none], self.password),
            "totp": from_union([from_str, from_none], self.totp),
        }
        return result

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @staticmethod
    def from_json(s: str) -> "Login":
        return Login.from_dict(json.loads(s))

    def to_file(self, path: str) -> None:
        with open(path, "w") as f:
            f.write(self.to_json())

    @staticmethod
    def from_file(path: str) -> "Login":
        with open(path, "r") as f:
            return Login.from_json(f.read())


@dataclass
class SecureNote:
    type: 0

    @staticmethod
    def from_dict(obj: Any) -> "SecureNote":
        assert isinstance(obj, dict)
        _type = from_union([from_int, from_none], obj.get("type"))
        return SecureNote(_type)

    def to_dict(self) -> dict:
        result: dict = {"type": from_union([from_int, from_none], self.type)}
        return result

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @staticmethod
    def from_json(s: str) -> "SecureNote":
        return SecureNote.from_dict(json.loads(s))

    def to_file(self, path: str) -> None:
        with open(path, "w") as f:
            f.write(self.to_json())

    @staticmethod
    def from_file(path: str) -> "SecureNote":
        with open(path, "r") as f:
            return SecureNote.from_json(f.read())


@dataclass
class Card:
    cardHolderName: Optional[str]
    brand: Optional[Enum]
    number: Optional[str]
    expMonth: Optional[str]
    expYear: Optional[str]
    code: Optional[str]

    @staticmethod
    def from_dict(obj: Any) -> "Card":
        assert isinstance(obj, dict)
        cardHolderName = from_union([from_str, from_none], obj.get("cardHolderName"))
        brand: CardType = CardType(obj.get("brand"))
        number = from_union([from_str, from_none], obj.get("number"))
        expMonth = from_union([from_str, from_none], obj.get("expMonth"))
        expYear = from_union([from_str, from_none], obj.get("expYear"))
        code = from_union([from_str, from_none], obj.get("code"))
        return Card(cardHolderName, brand, number, expMonth, expYear, code)

    def to_dict(self) -> dict:
        result: dict = {
            "cardHolderName": from_union([from_str, from_none], self.cardHolderName),
            "brand": to_enum(self.brand).value,
            "number": from_union([from_str, from_none], self.number),
            "expMonth": from_union([from_str, from_none], self.expMonth),
            "expYear": from_union([from_str, from_none], self.expYear),
            "code": from_union([from_str, from_none], self.code),
        }
        return result

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @staticmethod
    def from_json(s: str) -> "Card":
        return Card.from_dict(json.loads(s))

    def to_file(self, path: str) -> None:
        with open(path, "w") as f:
            f.write(self.to_json())

    @staticmethod
    def from_file(path: str) -> "Card":
        with open(path, "r") as f:
            return Card.from_json(f.read())


@dataclass
class Identity:
    title: Optional[str]
    firstName: Optional[str]
    middleName: Optional[str]
    lastName: Optional[str]
    address1: Optional[str]
    address2: Optional[str]
    address3: Optional[str]
    city: Optional[str]
    state: Optional[str]
    postalCode: Optional[str]
    country: Optional[str]
    company: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    ssn: Optional[str]
    username: Optional[str]
    passportNumber: Optional[str]
    licenseNumber: Optional[str]

    @staticmethod
    def from_dict(obj: Any) -> "Identity":
        assert isinstance(obj, dict)
        title = from_union([from_str, from_none], obj.get("title"))
        firstName = from_union([from_str, from_none], obj.get("firstName"))
        middleName = from_union([from_str, from_none], obj.get("middleName"))
        lastName = from_union([from_str, from_none], obj.get("lastName"))
        address1 = from_union([from_str, from_none], obj.get("address1"))
        address2 = from_union([from_str, from_none], obj.get("address2"))
        address3 = from_union([from_str, from_none], obj.get("address3"))
        city = from_union([from_str, from_none], obj.get("city"))
        state = from_union([from_str, from_none], obj.get("state"))
        postalCode = from_union([from_str, from_none], obj.get("postalCode"))
        country = from_union([from_str, from_none], obj.get("country"))
        company = from_union([from_str, from_none], obj.get("company"))
        email = from_union([from_str, from_none], obj.get("email"))
        phone = from_union([from_str, from_none], obj.get("phone"))
        ssn = from_union([from_str, from_none], obj.get("ssn"))
        username = from_union([from_str, from_none], obj.get("username"))
        passportNumber = from_union([from_str, from_none], obj.get("passportNumber"))
        licenseNumber = from_union([from_str, from_none], obj.get("licenseNumber"))
        return Identity(
            title,
            firstName,
            middleName,
            lastName,
            address1,
            address2,
            address3,
            city,
            state,
            postalCode,
            country,
            company,
            email,
            phone,
            ssn,
            username,
            passportNumber,
            licenseNumber,
        )

    def to_dict(self) -> dict:
        result: dict = {
            "title": from_union([from_str, from_none], self.title),
            "firstName": from_union([from_str, from_none], self.firstName),
            "middleName": from_union([from_str, from_none], self.middleName),
            "lastName": from_union([from_str, from_none], self.lastName),
            "address1": from_union([from_str, from_none], self.address1),
            "address2": from_union([from_str, from_none], self.address2),
            "address3": from_union([from_str, from_none], self.address3),
            "city": from_union([from_str, from_none], self.city),
            "state": from_union([from_str, from_none], self.state),
            "postalCode": from_union([from_str, from_none], self.postalCode),
            "country": from_union([from_str, from_none], self.country),
            "company": from_union([from_str, from_none], self.company),
            "email": from_union([from_str, from_none], self.email),
            "phone": from_union([from_str, from_none], self.phone),
            "ssn": from_union([from_str, from_none], self.ssn),
            "username": from_union([from_str, from_none], self.username),
            "passportNumber": from_union([from_str, from_none], self.passportNumber),
            "licenseNumber": from_union([from_str, from_none], self.licenseNumber),
        }
        return result

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @staticmethod
    def from_json(s: str) -> "Identity":
        return Identity.from_dict(json.loads(s))

    def to_file(self, path: str) -> None:
        with open(path, "w") as f:
            f.write(self.to_json())

    @staticmethod
    def from_file(path: str) -> "Identity":
        with open(path, "r") as f:
            return Identity.from_json(f.read())


@dataclass
class Field:
    name: Optional[str]
    value: Optional[str]
    type: Optional[Enum]

    @staticmethod
    def from_dict(obj: Any) -> "Field":
        assert isinstance(obj, dict)
        name = from_union([from_str, from_none], obj.get("name"))
        value = from_union([from_str, from_none], obj.get("value"))
        _type = from_union([ItemType, from_none], obj.get("type"))
        return Field(name, value, _type)

    def to_dict(self) -> dict:
        result: dict = {
            "name": from_union([from_str, from_none], self.name),
            "value": from_union([from_str, from_none], self.value),
            "type": from_union([lambda x: to_enum(x), from_none], self.type),
        }
        return result

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @staticmethod
    def from_json(s: str) -> "Field":
        return Field.from_dict(json.loads(s))

    def to_file(self, path: str) -> None:
        with open(path, "w") as f:
            f.write(self.to_json())

    @staticmethod
    def from_file(path: str) -> "Field":
        with open(path, "r") as f:
            return Field.from_json(f.read())


@dataclass
class Item:
    organizationId: Optional[str]
    collectionId: Optional[str]
    folderId: Optional[str]
    type: ItemType
    name: str
    notes: Optional[str]
    favorite: bool
    fields: Optional[Field]
    login: Optional[Login]
    secureNote: Optional[SecureNote]
    card: Optional[Card]
    identity: Optional[Identity]
    reprompt: bool
    object: str = "item"
    id: str = None

    @staticmethod
    def from_dict(obj: Any) -> "Item":
        assert isinstance(obj, dict)
        organizationId = from_str(obj.get("organizationId"))
        collectionId = (
            from_str(obj.get("collectionId")) if obj.get("collectionId") else []
        )
        folderId = from_str(obj.get("folderId"))
        _type: ItemType = ItemType(obj.get("type"))
        name = from_str(obj.get("name"))
        notes = from_union([from_str, from_none], obj.get("notes"))
        favorite = from_bool(obj.get("favorite"))
        fields = from_union([Field.from_dict, from_none], obj.get("fields"))
        login = from_union([Login.from_dict, from_none], obj.get("login"))
        secureNote = from_union(
            [SecureNote.from_dict, from_none], obj.get("secureNote")
        )
        card = from_union([Card.from_dict, from_none], obj.get("card"))
        identity = from_union([Identity.from_dict, from_none], obj.get("identity"))
        reprompt = from_bool(obj.get("reprompt")).__int__()
        _object = from_str(obj.get("object"))
        _id = from_str(obj.get("id"))
        return Item(
            organizationId,
            collectionId,
            folderId,
            _type,
            name,
            notes,
            favorite,
            fields,
            login,
            secureNote,
            card,
            identity,
            reprompt,
            _object,
            _id,
        )

    def to_dict(self) -> dict:
        result: dict = {
            "organizationId": from_str(self.organizationId),
            "collectionId": from_str(self.collectionId if self.collectionId else []),
            "folderId": from_str(self.folderId),
            "type": to_enum(self.type).value,
            "name": from_str(self.name),
            "notes": from_str(self.notes),
            "favorite": from_bool(self.favorite),
            "fields": from_union(
                [lambda x: to_class(Field, x), from_none], self.fields
            ),
            "login": from_union([lambda x: to_class(Login, x), from_none], self.login),
            "secureNote": from_union(
                [lambda x: to_class(SecureNote, x), from_none], self.secureNote
            ),
            "card": from_union([lambda x: to_class(Card, x), from_none], self.card),
            "identity": from_union(
                [lambda x: to_class(Identity, x), from_none], self.identity
            ),
            "reprompt": from_bool(self.reprompt).__int__(),
            "object": from_str(self.object),
            "id": from_str(self.id),
        }

        if self.type == ItemType.LOGIN:
            result.pop("secureNote")
            result.pop("card")
            result.pop("identity")
        elif self.type == ItemType.SECURE_NOTE:
            result.pop("login")
            result.pop("card")
            result.pop("identity")
        elif self.type == ItemType.CARD:
            result.pop("login")
            result.pop("secureNote")
            result.pop("identity")
        elif self.type == ItemType.IDENTITY:
            result.pop("login")
            result.pop("secureNote")
            result.pop("card")
        return result

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, cls=CustomEncoder)

    @staticmethod
    def from_json(s: str) -> "Item":
        return Item.from_dict(json.loads(s))

    def to_file(self, path: str) -> None:
        with open(path, "w") as f:
            f.write(self.to_json())

    @staticmethod
    def from_file(path: str) -> "Item":
        with open(path, "r") as f:
            return Item.from_json(f.read())


@dataclass
class OrgMember:  # @TODO: test this
    object: str
    email: str
    name: str
    id: str
    status: int
    type: MemberType
    twoFactorEnabled: bool

    @staticmethod
    def from_dict(data: dict) -> "OrgMember":
        return OrgMember(
            object=data.get("object", None),
            email=data.get("email", None),
            name=data.get("name", None),
            id=data.get("id", None),
            status=data.get("status", None),
            type=data.get("type", None),
            twoFactorEnabled=data.get("twoFactorEnabled", None),
        )

    def to_dict(self) -> dict:
        return {
            "object": self.object,
            "email": self.email,
            "name": self.name,
            "id": self.id,
            "status": self.status,
            "type": self.type,
            "twoFactorEnabled": self.twoFactorEnabled,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @staticmethod
    def from_json(s: str) -> "OrgMember":
        return OrgMember.from_dict(json.loads(s))

    def to_file(self, path: str) -> None:
        with open(path, "w") as f:
            f.write(self.to_json())

    @staticmethod
    def from_file(path: str) -> "OrgMember":
        with open(path, "r") as f:
            return OrgMember.from_json(f.read())


@dataclass
class Group:
    id: str
    readOnly: bool
    hidePasswords: bool

    @staticmethod
    def from_dict(obj: Any) -> "Group":
        assert isinstance(obj, dict)
        _id = from_str(obj.get("id"))
        readOnly = from_bool(obj.get("readOnly"))
        hidePasswords = from_bool(obj.get("hidePasswords"))
        return Group(_id, readOnly, hidePasswords)

    def to_dict(self) -> dict:
        result: dict = {
            "id": from_str(self.id),
            "readOnly": from_bool(self.readOnly),
            "hidePasswords": from_bool(self.hidePasswords),
        }
        return result

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @staticmethod
    def from_json(s: str) -> "Group":
        return Group.from_dict(json.loads(s))

    def to_file(self, path: str) -> None:
        with open(path, "w") as f:
            f.write(self.to_json())

    @staticmethod
    def from_file(path: str) -> "Group":
        with open(path, "r") as f:
            return Group.from_json(f.read())


@dataclass
class Folder:
    name: str
    id: str = None
    object: str = "folder"

    @staticmethod
    def from_dict(obj: Any) -> "Folder":
        assert isinstance(obj, dict)
        name = from_str(obj.get("name"))
        _id = from_str(obj.get("id"))
        _object = from_str(obj.get("object"))
        return Folder(name)

    def to_dict(self) -> dict:
        result: dict = {
            "name": from_str(self.name),
            "id": from_str(self.id) if self.id else None,
            "object": from_str(self.object),
        }
        return result

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @staticmethod
    def from_json(s: str) -> "Folder":
        return Folder.from_dict(json.loads(s))

    def to_file(self, path: str) -> None:
        with open(path, "w") as f:
            f.write(self.to_json())

    @staticmethod
    def from_file(path: str) -> "Folder":
        with open(path, "r") as f:
            return Folder.from_json(f.read())


@dataclass
class Collection:
    organizationId: Optional[str]
    name: str
    externalId: Optional[str]
    groups: Optional[List[Group]]

    @staticmethod
    def from_dict(obj: Any) -> "Collection":
        assert isinstance(obj, dict)
        organizationId = from_str(obj.get("organizationId"))
        name = from_str(obj.get("name"))
        externalId = from_str(obj.get("externalId"))
        groups = from_union(
            [lambda x: from_list(Group.from_dict, x), from_none], obj.get("groups")
        )
        return Collection(organizationId, name, externalId, groups)

    def to_dict(self) -> dict:
        result: dict = {
            "organizationId": from_str(self.organizationId),
            "name": from_str(self.name),
            "externalId": from_str(self.externalId),
            "groups": from_union(
                [lambda x: from_list(lambda y: to_class(Group, y), x), from_none],
                self.groups,
            ),
        }
        return result

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @staticmethod
    def from_json(s: str) -> "Collection":
        return Collection.from_dict(json.loads(s))

    def to_file(self, path: str) -> None:
        with open(path, "w") as f:
            f.write(self.to_json())

    @staticmethod
    def from_file(path: str) -> "Collection":
        with open(path, "r") as f:
            return Collection.from_json(f.read())


@dataclass
class SendText:
    text: str
    hidden: bool

    @staticmethod
    def from_dict(obj: Any) -> "SendText":
        assert isinstance(obj, dict)
        text = from_str(obj.get("text"))
        hidden = from_bool(obj.get("hidden"))
        return SendText(text, hidden)

    def to_dict(self) -> dict:
        result: dict = {"text": from_str(self.text), "hidden": from_bool(self.hidden)}
        return result

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @staticmethod
    def from_json(s: str) -> "SendText":
        return SendText.from_dict(json.loads(s))

    def to_file(self, path: str) -> None:
        with open(path, "w") as f:
            f.write(self.to_json())

    @staticmethod
    def from_file(path: str) -> "SendText":
        with open(path, "r") as f:
            return SendText.from_json(f.read())


@dataclass
class Send:
    name: str
    notes: Optional[str]
    type: SendType
    text: Optional[SendText]
    file: Optional[str]
    maxAccessCount: Optional[int]
    deletionDate: Optional[datetime.datetime]
    expirationDate: Optional[datetime.datetime]
    password: Optional[str]
    disabled: bool
    hideEmail: bool

    @staticmethod
    def from_dict(obj: Any) -> "Send":
        assert isinstance(obj, dict)
        name = from_str(obj.get("name"))
        notes = from_union([from_str, from_none], obj.get("notes"))
        _type = SendType(obj.get("type"))
        text = from_union([SendText.from_dict, from_none], obj.get("text"))
        file = from_union([from_str, from_none], obj.get("file"))
        maxAccessCount = from_union([from_int, from_none], obj.get("maxAccessCount"))
        deletionDateStr = obj.get("deletionDate")
        deletionDate = None
        if deletionDateStr is not None:
            try:
                deletionDate = datetime.datetime.strptime(
                    deletionDateStr, "%Y-%m-%dT%H:%M:%S.%fZ"
                )
            except ValueError:
                raise ValueError(
                    f"Invalid deletion date format: {deletionDateStr}. Expected format: %Y-%m-%dT%H:%M:%S.%fZ"
                )
        expirationDateStr = obj.get("expirationDate")
        expirationDate = None
        if expirationDateStr is not None:
            try:
                expirationDate = datetime.datetime.strptime(
                    expirationDateStr, "%Y-%m-%dT%H:%M:%S.%fZ"
                )
            except ValueError:
                raise ValueError(
                    f"Invalid expiration date format: {expirationDateStr}. Expected format: %Y-%m-%dT%H:%M:%S.%fZ"
                )
        password = from_union([from_str, from_none], obj.get("password"))
        disabled = from_union([from_bool, from_none], obj.get("disabled"))
        hideEmail = from_union([from_bool, from_none], obj.get("hideEmail"))
        return Send(
            name,
            notes,
            _type,
            text,
            file,
            maxAccessCount,
            deletionDate,
            expirationDate,
            password,
            disabled,
            hideEmail,
        )

    def to_dict(self) -> dict:
        result: dict = {
            "name": from_str(self.name),
            "notes": from_union([from_str, from_none], self.notes),
            "type": to_enum(self.type).value,
            "text": from_union([lambda x: to_class(SendText, x), from_none], self.text),
            "file": from_union([from_str, from_none], self.file),
            "maxAccessCount": from_union([from_int, from_none], self.maxAccessCount),
            "deletionDate": str(self.deletionDate) if self.deletionDate else None,
            "expirationDate": str(self.expirationDate) if self.expirationDate else None,
            "password": from_union([from_str, from_none], self.password),
            "disabled": from_union([from_bool, from_none], self.disabled),
            "hideEmail": from_union([from_bool, from_none], self.hideEmail),
        }
        return result

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @staticmethod
    def from_json(s: str) -> "Send":
        return Send.from_dict(json.loads(s))

    def to_file(self, path: str) -> None:
        with open(path, "w") as f:
            f.write(self.to_json())

    @staticmethod
    def from_file(path: str) -> "Send":
        with open(path, "r") as f:
            return Send.from_json(f.read())


# HTTP methods
def get(url: str, headers=None) -> dict:
    if headers is None:
        headers = {}
    response = requests.get(url, headers=headers)
    return response.json()


def post(url: str, data: dict = None, headers=None) -> dict:
    if headers is None:
        headers = {}
    response = requests.post(url, json=data, headers=headers)
    return response.json()


def post_file(url: str, file: str, headers=None) -> Response:
    if headers is None:
        headers = {}
    with open(file, "rb") as f:
        response = requests.post(url, files=f, headers=headers)
    return response  # .json()


def put(url: str, data: dict, headers=None) -> dict:
    if headers is None:
        headers = {}
    response = requests.put(url, json=data, headers=headers)
    return response.json()


def put_file(url: str, file: str, headers=None):  # @TODO: add return type
    if headers is None:
        headers = {}
    with open(file, "rb") as f:
        response = requests.put(url, files=f, headers=headers)
    return response  # .json()


def delete(url: str, headers=None) -> dict:
    if headers is None:
        headers = {}
    response = requests.delete(url, headers=headers)
    return response.json()


# Other functions
def print_json(data: dict) -> None:
    print(json.dumps(data, indent=2, sort_keys=True))


### Lock & Unlock ###
def lock() -> dict:
    return post(f"{BW_SERVER_URL}/lock")


def unlock(password: str) -> dict:
    return post(f"{BW_SERVER_URL}/unlock", data={"password": password})


### Miscellaneous ###
def sync() -> dict:
    return post(f"{BW_SERVER_URL}/sync")


def status() -> dict:
    return get(f"{BW_SERVER_URL}/status")


def get_generate() -> dict:
    return get(f"{BW_SERVER_URL}/generate")


def get_template(template: str) -> dict:
    return get(f"{BW_SERVER_URL}/object/template/{template}")


def get_fingerprint() -> dict:
    return get(f"{BW_SERVER_URL}/object/fingerprint/me")


### Vault Items ###
def get_item(_id: str) -> Item:
    response = get(f"{BW_SERVER_URL}/object/item/{_id}")
    if response["data"]["object"] == "item":
        item = Item.from_dict(response.get("data"))
        return item
    else:
        raise Exception("Not an item")


def add_item(item: Item) -> Item:
    response = post(f"{BW_SERVER_URL}/object/item", data=item.to_dict())
    if response["data"]["object"] == "item":
        item = Item.from_dict(response.get("data"))
        return item
    else:
        raise Exception("Not an item")


def edit_item(_id: str, item: Item) -> Item:
    response = put(f"{BW_SERVER_URL}/object/item/{_id}", data=item.to_dict())
    if response["data"]["object"] == "item":
        item = Item.from_dict(response.get("data"))
        return item
    else:
        raise Exception("Not an item")


def delete_item(_id: str) -> dict:
    return delete(f"{BW_SERVER_URL}/object/item/{_id}")


def restore_item(_id: str) -> dict:
    return post(f"{BW_SERVER_URL}/restore/item/{_id}")


def get_items() -> List[Item]:
    response = get(f"{BW_SERVER_URL}/list/object/items")
    if response["data"]["object"] == "list":
        items = []
        for item in response["data"]["data"]:
            items.append(Item.from_dict(item))
        return items
    else:
        raise Exception("Not a list")


### Attachments & Fields ###
def add_attachment(_id: str, file: str) -> Response:
    return post_file(f"{BW_SERVER_URL}/object/attachment?itemid={_id}", file)


def get_attachment(_id: str, attachmentId: str) -> dict:
    return get(
        f"{BW_SERVER_URL}/object/attachment/{attachmentId}?itemid={_id}",
        headers={"Accept": "*/*"},
    )


def delete_attachment(_id: str, attachmentId: str) -> dict:
    return delete(f"{BW_SERVER_URL}/object/attachment/{attachmentId}?itemid={_id}")


def get_username(_id: str, onlyValue: bool = False) -> Union[dict, Response]:
    response = get(f"{BW_SERVER_URL}/object/username/{_id}")
    if onlyValue:
        return response["data"]["data"]
    else:
        return response


def get_password(_id: str, onlyValue: bool = False) -> Union[dict, Response]:
    response = get(f"{BW_SERVER_URL}/object/password/{_id}")
    if onlyValue:
        return response["data"]["data"]
    else:
        return response


def get_totp(_id: str, onlyValue: bool = False) -> Union[dict, Response]:
    response = get(f"{BW_SERVER_URL}/object/totp/{_id}")
    if onlyValue:
        try:
            return response["data"]["data"]
        except KeyError:
            return response["message"]
    else:
        return response


def get_notes(_id: str, onlyValue: bool = False) -> Union[dict, Response]:
    response = get(f"{BW_SERVER_URL}/object/notes/{_id}")
    if onlyValue:
        try:
            return response["data"]["data"]
        except KeyError:
            return response["message"]
    else:
        return response


def get_exposed(_id: str, onlyValue: bool = False) -> Union[dict, Response]:
    response = get(f"{BW_SERVER_URL}/object/exposed/{_id}")
    if onlyValue:
        return response["data"]["data"]
    else:
        return response


### Folders ###
def add_folder(name: str) -> Folder:
    response = post(f"{BW_SERVER_URL}/object/folder", data={"name": name})
    if response["data"]["object"] == "folder":
        return Folder.from_dict(response.get("data"))
    else:
        raise Exception("Not a folder")


def edit_folder(_id: str, name: str) -> Folder:
    response = put(f"{BW_SERVER_URL}/object/folder/{_id}", data={"name": name})
    if response["data"]["object"] == "folder":
        return Folder.from_dict(response.get("data"))
    else:
        raise Exception("Not a folder")


def get_folder(_id: str) -> Folder:
    response = get(f"{BW_SERVER_URL}/object/folder/{_id}")
    if response["data"]["object"] == "folder":
        return Folder.from_dict(response.get("data"))
    else:
        raise Exception("Not a folder")


def delete_folder(_id: str) -> dict:
    return delete(f"{BW_SERVER_URL}/object/folder/{_id}")


def get_folders() -> List[Folder]:
    response = get(f"{BW_SERVER_URL}/list/object/folders")
    folders = []
    for folder in response["data"]["data"]:
        folders.append(Folder.from_dict(folder))
    return folders


### Sends ###
def add_send(send: Send) -> Send:
    send_dict = send.to_dict()
    response = post(f"{BW_SERVER_URL}/object/send", data=send_dict)
    if not isinstance(response, dict) or "data" not in response:
        raise Exception("Invalid server response: Missing or invalid 'data' field")
    try:
        send_obj = Send.from_dict(response["data"])
        return send_obj
    except KeyError:
        raise Exception("Error creating Send object")


def edit_send(_id: str, send: Send) -> Send:
    send_dict = send.to_dict()
    response = put(f"{BW_SERVER_URL}/object/send/{_id}", data=send_dict)
    if not isinstance(response, dict) or "data" not in response:
        raise Exception("Invalid server response: Missing or invalid 'data' field")
    try:
        send_obj = Send.from_dict(response["data"])
        return send_obj
    except KeyError:
        raise Exception("Error creating Send object")


def get_send(_id: str) -> Send:
    response = get(f"{BW_SERVER_URL}/object/send/{_id}")
    if not isinstance(response, dict) or "data" not in response:
        raise Exception("Invalid server response: Missing or invalid 'data' field")
    try:
        send_obj = Send.from_dict(response["data"])
        return send_obj
    except KeyError:
        raise Exception("Error creating Send object")


def delete_send(_id: str) -> dict:
    return delete(f"{BW_SERVER_URL}/object/send/{_id}")


def get_sends() -> List[Send]:
    response = get(f"{BW_SERVER_URL}/list/object/send")
    if not isinstance(response, dict) or "data" not in response:
        raise Exception("Invalid server response: Missing or invalid 'data' field")
    sends = []
    for send in response["data"]["data"]:
        sends.append(Send.from_dict(send))
    return sends


def remove_password(_id: str) -> dict:
    return post(f"{BW_SERVER_URL}/send/{_id}/remove-password")


### Collections & Organizations ### # @TODO: test these
def move_item(
    item_id: str, org_id: str, collections: List[str]
) -> dict:  # @TODO: make collections a list of Collection objects
    return post(
        f"{BW_SERVER_URL}/move/{item_id}/{org_id}",
        data={"collections": collections},
    )


def add_org_collection(org_id: str, collection: Collection) -> Collection:
    collection_dict = collection.to_dict()
    response = post(
        f"{BW_SERVER_URL}/object/org-collection?organizationId={org_id}",
        # @TODO: organizationId might be organizationid
        data=collection_dict,
    )
    if not isinstance(response, dict) or "data" not in response:
        raise Exception("Invalid server response: Missing or invalid 'data' field")
    try:
        collection_obj = Collection.from_dict(response["data"])
        return collection_obj
    except KeyError:
        raise Exception("Error creating Collection object")


def edit_org_collection(
    org_id: str, collection_id: str, collection: Collection
) -> Collection:
    collection_dict = collection.to_dict()
    response = put(
        f"{BW_SERVER_URL}/object/org-collection/{collection_id}?organizationId={org_id}",
        # @TODO: organizationId might be organizationid
        data=collection_dict,
    )
    if not isinstance(response, dict) or "data" not in response:
        raise Exception("Invalid server response: Missing or invalid 'data' field")
    try:
        collection_obj = Collection.from_dict(response["data"])
        return collection_obj
    except KeyError:
        raise Exception("Error creating Collection object")


def get_org_collection(org_id: str, collection_id: str) -> Collection:
    response = get(
        f"{BW_SERVER_URL}/object/org-collection/{collection_id}?organizationId={org_id}"
        # @TODO: organizationId might be organizationid
    )
    if not isinstance(response, dict) or "data" not in response:
        raise Exception("Invalid server response: Missing or invalid 'data' field")
    try:
        collection_obj = Collection.from_dict(response["data"])
        return collection_obj
    except KeyError:
        raise Exception("Error creating Collection object")


def delete_org_collection(org_id: str, collection_id: str) -> dict:
    return delete(
        f"{BW_SERVER_URL}/object/org-collection/{collection_id}?organizationId={org_id}"
        # @TODO: organizationId might be organizationid
    )


def get_org_collections(org_id: str) -> List[Collection]:
    response = get(
        f"{BW_SERVER_URL}/list/object/org-collections?organizationId={org_id}"
        # @TODO: organizationId might be organizationid
    )
    if not isinstance(response, dict) or "data" not in response:
        raise Exception("Invalid server response: Missing or invalid 'data' field")
    collections = []
    for collection in response["data"]["data"]:
        collections.append(Collection.from_dict(collection))
    return collections


def get_collections(search_query: str = None) -> List[Collection]:
    if search_query:
        response = get(f"{BW_SERVER_URL}/list/object/collections?search={search_query}")
    else:
        response = get(f"{BW_SERVER_URL}/list/object/collections")
    if not isinstance(response, dict) or "data" not in response:
        raise Exception("Invalid server response: Missing or invalid 'data' field")
    collections = []
    for collection in response["data"]["data"]:
        collections.append(Collection.from_dict(collection))
    return collections


def get_organizations(search_query: str = None) -> list:
    if search_query:
        response = get(
            f"{BW_SERVER_URL}/list/object/organizations?search={search_query}"
        )
    else:
        response = get(f"{BW_SERVER_URL}/list/object/organizations")
    if not isinstance(response, dict) or "data" not in response:
        raise Exception("Invalid server response: Missing or invalid 'data' field")
    organizations = []
    for organization in response["data"]["data"]:
        # we don't have an Organization class
        organizations.append(organization)
    return organizations


def get_org_members(org_id: str) -> List[OrgMember]:
    response = get(f"{BW_SERVER_URL}/list/object/org-members/{org_id}")
    if not isinstance(response, dict) or "data" not in response:
        raise Exception("Invalid server response: Missing or invalid 'data' field")
    members = []
    for member in response["data"]["data"]:
        members.append(OrgMember.from_dict(member))
    return members


def confirm_org_member(org_id: str, member_id: str) -> dict:
    return post(
        f"{BW_SERVER_URL}/confirm/org-member/{member_id}?organizationId={org_id}"
        # @TODO: organizationId might be organizationid
    )


# Run
LOGIN_ITEM: Item = Item(
    organizationId=None,
    collectionId=None,
    folderId=None,
    type=ItemType.LOGIN,
    name="Login Item",
    notes=None,
    favorite=False,
    fields=None,
    login=Login(
        uris=[
            Uri(match=MatchType.DOMAIN, uri="https://wikipedia.org"),
            Uri(match=MatchType.EXACT, uri="https://archive.org"),
        ],
        username="username123",
        password="password123",
        totp="totp1234",
    ),
    secureNote=None,
    card=None,
    identity=None,
    reprompt=False,
)

SECURENOTE_ITEM: Item = Item(
    organizationId=None,
    collectionId=None,
    folderId=None,
    type=ItemType.SECURE_NOTE,
    name="Secure Note Item",
    notes="The quick brown fox jumps over the lazy dog.",
    favorite=False,
    fields=None,
    login=None,
    secureNote=SecureNote(type=0),
    card=None,
    identity=None,
    reprompt=False,
)

CARD_ITEM: Item = Item(
    organizationId=None,
    collectionId=None,
    folderId=None,
    type=ItemType.CARD,
    name="Card Item",
    notes=None,
    favorite=False,
    fields=None,
    login=None,
    secureNote=None,
    card=Card(
        cardHolderName="John Brown",
        brand=CardType.VISA,
        number="4111111111111111",
        expMonth="12",
        expYear="2032",
        code="666",
    ),
    identity=None,
    reprompt=False,
)

IDENTITY_ITEM: Item = Item(
    organizationId=None,
    collectionId=None,
    folderId=None,
    type=ItemType.IDENTITY,
    name="Identity Item",
    notes=None,
    favorite=False,
    fields=None,
    login=None,
    secureNote=None,
    card=None,
    identity=Identity(
        title="Dr.",
        firstName="John",
        middleName=None,
        lastName="Brown",
        address1="123 Main St.",
        address2=None,
        address3=None,
        city="Charles Town",
        state="WV",
        postalCode="25414",
        country="USA",
        company=None,
        email="ididnothingwrong@nicetry.meme",
        phone="304-555-5555",
        ssn=None,
        username=None,
        passportNumber=None,
        licenseNumber=None,
    ),
    reprompt=False,
)

TEXT_SEND: Send = Send(
    name="Derek Zoolander Sender for Children Who Can't Read Good and Who Wanna Learn to Do Other Stuff Good Too",
    notes="A send for ants.",
    type=SendType.TEXT,
    text=SendText(text="WHAT IS THIS? A SEND FOR ANTS?", hidden=False),
    file=None,
    maxAccessCount=None,
    deletionDate=datetime.datetime.now()
    + datetime.timedelta(
        days=7
    ),  # @TODO: investigate potential bug with API not allowing None
    expirationDate=datetime.datetime.now()
    + datetime.timedelta(
        days=6
    ),  # @TODO: investigate potential bug with API not allowing None
    password="password123",
    disabled=False,
    hideEmail=False,
)

# FILE_SEND = Send('Creating a file-based Send is unsupported through the `serve` command at this time.')

# # print_json(lock())
# # print_json(
# unlock(PASSWORD)
# # )
# # print_json(status())
# # print_json(get_template("item.login"))
# # print_json(get_fingerprint())
# # print_json(get_generate())
# # print_json(sync())
# # print_json(item_dict)
# # print_json(LOGIN_ITEM)
# (get_item("826cd361-6624-4e30-8a12-b04d016f5a5d").to_json())
# (add_item(LOGIN_ITEM).to_json())
# (add_item(SECURENOTE_ITEM))
# (add_item(CARD_ITEM))
# (add_item(IDENTITY_ITEM))
# (edit_item("826cd361-6624-4e30-8a12-b04d016f5a5d", LOGIN_ITEM).to_json())
# # print_json(delete_item("bc1243a3-8942-4ade-b261-b04d017119de"))
# # print_json(restore_item("bc1243a3-8942-4ade-b261-b04d017119de"))
# (get_items())
# # # add_attachment(
# # #     "826cd361-6624-4e30-8a12-b04d016f5a5d", "tmp.delete"
# # # )  # @TODO: verify that this works with a Premium account
# # # get_attachment("826cd361-6624-4e30-8a12-b04d016f5a5d", "b04d016f5a5d")
# # # delete_attachment("826cd361-6624-4e30-8a12-b04d016f5a5d", "b04d016f5a5d")
# (get_username("826cd361-6624-4e30-8a12-b04d016f5a5d", True))
# (get_password("826cd361-6624-4e30-8a12-b04d016f5a5d", True))
# (get_totp("826cd361-6624-4e30-8a12-b04d016f5a5d", True))  # requires Premium
# (get_notes("826cd361-6624-4e30-8a12-b04d016f5a5d", True))
# (
#     get_exposed("826cd361-6624-4e30-8a12-b04d016f5a5d", True)
# )  # requires Premium; return "251682"???
# (add_folder("Test Folder").to_dict())
# (edit_folder("ec9dc6fa-8902-4a1e-8124-b04d01842044", "Edited Test Folder").to_dict())
# (get_folder("ec9dc6fa-8902-4a1e-8124-b04d01842044").to_dict())
# # print_json(delete_folder("ec9dc6fa-8902-4a1e-8124-b04d01842044"))
# # print(get_folders())
# (add_send(TEXT_SEND))
# (edit_send("5d29993f-bfaa-4ce4-a3ca-b04e00d244ea", TEXT_SEND))
# (get_send("5d29993f-bfaa-4ce4-a3ca-b04e00d244ea"))
# # (delete_send("01b04f48-e7d5-4b8f-9aca-b04e00d2d8d8"))
# (get_sends())
# (remove_password("4c7be01d-488b-4ef7-9a81-b04e00eb10b7"))
