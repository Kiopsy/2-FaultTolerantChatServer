# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: chat_service.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x12\x63hat_service.proto\x12\x04\x63hat\"A\n\x0bSendRequest\x12\x0e\n\x06sender\x18\x01 \x01(\t\x12\x11\n\trecipient\x18\x02 \x01(\t\x12\x0f\n\x07\x63ontent\x18\x03 \x01(\t\"0\n\x0cSendResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\x12\x0f\n\x07message\x18\x02 \x01(\t\"\x07\n\x05\x45mpty\".\n\x0b\x43hatMessage\x12\x0e\n\x06sender\x18\x01 \x01(\t\x12\x0f\n\x07\x63ontent\x18\x02 \x01(\t\"\x18\n\x04User\x12\x10\n\x08username\x18\x01 \x01(\t\"2\n\x0cLoginRequest\x12\x10\n\x08username\x18\x01 \x01(\t\x12\x10\n\x08password\x18\x02 \x01(\t\"1\n\rLoginResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\x12\x0f\n\x07message\x18\x02 \x01(\t\"5\n\x0fRegisterRequest\x12\x10\n\x08username\x18\x01 \x01(\t\x12\x10\n\x08password\x18\x02 \x01(\t\"4\n\x10RegisterResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\x12\x0f\n\x07message\x18\x02 \x01(\t\"!\n\rDeleteRequest\x12\x10\n\x08username\x18\x01 \x01(\t\"2\n\x0e\x44\x65leteResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\x12\x0f\n\x07message\x18\x02 \x01(\t2\xa3\x01\n\x0b\x43hatService\x12\x36\n\x0bSendMessage\x12\x11.chat.SendRequest\x1a\x12.chat.SendResponse\"\x00\x12\x33\n\x0eReceiveMessage\x12\n.chat.User\x1a\x11.chat.ChatMessage\"\x00\x30\x01\x12\'\n\x08GetUsers\x12\x0b.chat.Empty\x1a\n.chat.User\"\x00\x30\x01\x32\xb5\x01\n\x0b\x41uthService\x12\x32\n\x05Login\x12\x12.chat.LoginRequest\x1a\x13.chat.LoginResponse\"\x00\x12;\n\x08Register\x12\x15.chat.RegisterRequest\x1a\x16.chat.RegisterResponse\"\x00\x12\x35\n\x06\x44\x65lete\x12\x13.chat.DeleteRequest\x1a\x14.chat.DeleteResponse\"\x00\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'chat_service_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _SENDREQUEST._serialized_start=28
  _SENDREQUEST._serialized_end=93
  _SENDRESPONSE._serialized_start=95
  _SENDRESPONSE._serialized_end=143
  _EMPTY._serialized_start=145
  _EMPTY._serialized_end=152
  _CHATMESSAGE._serialized_start=154
  _CHATMESSAGE._serialized_end=200
  _USER._serialized_start=202
  _USER._serialized_end=226
  _LOGINREQUEST._serialized_start=228
  _LOGINREQUEST._serialized_end=278
  _LOGINRESPONSE._serialized_start=280
  _LOGINRESPONSE._serialized_end=329
  _REGISTERREQUEST._serialized_start=331
  _REGISTERREQUEST._serialized_end=384
  _REGISTERRESPONSE._serialized_start=386
  _REGISTERRESPONSE._serialized_end=438
  _DELETEREQUEST._serialized_start=440
  _DELETEREQUEST._serialized_end=473
  _DELETERESPONSE._serialized_start=475
  _DELETERESPONSE._serialized_end=525
  _CHATSERVICE._serialized_start=528
  _CHATSERVICE._serialized_end=691
  _AUTHSERVICE._serialized_start=694
  _AUTHSERVICE._serialized_end=875
# @@protoc_insertion_point(module_scope)
