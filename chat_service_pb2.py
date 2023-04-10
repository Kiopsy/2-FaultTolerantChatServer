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




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x12\x63hat_service.proto\x12\x04\x63hat\"Y\n\nReviveInfo\x12\x14\n\x0cprimary_port\x18\x01 \x01(\x03\x12\x12\n\ncommit_log\x18\x02 \x01(\t\x12\x10\n\x08\x64\x62_bytes\x18\x03 \x01(\x0c\x12\x0f\n\x07updates\x18\x04 \x01(\x08\"\x07\n\x05\x45mpty\"2\n\x11HeartbeatResponse\x12\x0c\n\x04port\x18\x01 \x01(\x03\x12\x0f\n\x07primary\x18\x02 \x01(\x08\"2\n\rCommitRequest\x12\x0e\n\x06\x63ommit\x18\x01 \x01(\t\x12\x11\n\tballot_id\x18\x02 \x01(\x03\"@\n\nCommitVote\x12\x0f\n\x07\x61pprove\x18\x01 \x01(\x08\x12\x0e\n\x06\x63ommit\x18\x02 \x01(\t\x12\x11\n\tballot_id\x18\x03 \x01(\x03\"\"\n\nTwoNumbers\x12\t\n\x01\x61\x18\x01 \x01(\x03\x12\t\n\x01\x62\x18\x02 \x01(\x03\"\x12\n\x03Sum\x12\x0b\n\x03sum\x18\x01 \x01(\x03\"A\n\x0bSendRequest\x12\x0e\n\x06sender\x18\x01 \x01(\t\x12\x11\n\trecipient\x18\x02 \x01(\t\x12\x0f\n\x07\x63ontent\x18\x03 \x01(\t\"0\n\x0cSendResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\x12\x0f\n\x07message\x18\x02 \x01(\t\".\n\x0b\x43hatMessage\x12\x0e\n\x06sender\x18\x01 \x01(\t\x12\x0f\n\x07\x63ontent\x18\x02 \x01(\t\"\x18\n\x04User\x12\x10\n\x08username\x18\x01 \x01(\t\"2\n\x0cLoginRequest\x12\x10\n\x08username\x18\x01 \x01(\t\x12\x10\n\x08password\x18\x02 \x01(\t\"1\n\rLoginResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\x12\x0f\n\x07message\x18\x02 \x01(\t\"5\n\x0fRegisterRequest\x12\x10\n\x08username\x18\x01 \x01(\t\x12\x10\n\x08password\x18\x02 \x01(\t\"4\n\x10RegisterResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\x12\x0f\n\x07message\x18\x02 \x01(\t\"!\n\rDeleteRequest\x12\x10\n\x08username\x18\x01 \x01(\t\"2\n\x0e\x44\x65leteResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\x12\x0f\n\x07message\x18\x02 \x01(\t2\xeb\x04\n\x0b\x43hatService\x12(\n\x05\x41live\x12\x0b.chat.Empty\x1a\x10.chat.ReviveInfo\"\x00\x12:\n\x10RequestHeartbeat\x12\x0b.chat.Empty\x1a\x17.chat.HeartbeatResponse\"\x00\x12\x38\n\rProposeCommit\x12\x13.chat.CommitRequest\x1a\x10.chat.CommitVote\"\x00\x12\x31\n\x0eSendVoteResult\x12\x10.chat.CommitVote\x1a\x0b.chat.Empty\"\x00\x12\"\n\x04Ping\x12\x0b.chat.Empty\x1a\x0b.chat.Empty\"\x00\x12)\n\x08\x41\x64\x64ition\x12\x10.chat.TwoNumbers\x1a\t.chat.Sum\"\x00\x12\x36\n\x0bSendMessage\x12\x11.chat.SendRequest\x1a\x12.chat.SendResponse\"\x00\x12\x31\n\x0eReceiveMessage\x12\n.chat.User\x1a\x11.chat.ChatMessage\"\x00\x12\'\n\x08GetUsers\x12\x0b.chat.Empty\x1a\n.chat.User\"\x00\x30\x01\x12\x32\n\x05Login\x12\x12.chat.LoginRequest\x1a\x13.chat.LoginResponse\"\x00\x12;\n\x08Register\x12\x15.chat.RegisterRequest\x1a\x16.chat.RegisterResponse\"\x00\x12\x35\n\x06\x44\x65lete\x12\x13.chat.DeleteRequest\x1a\x14.chat.DeleteResponse\"\x00\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'chat_service_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _REVIVEINFO._serialized_start=28
  _REVIVEINFO._serialized_end=117
  _EMPTY._serialized_start=119
  _EMPTY._serialized_end=126
  _HEARTBEATRESPONSE._serialized_start=128
  _HEARTBEATRESPONSE._serialized_end=178
  _COMMITREQUEST._serialized_start=180
  _COMMITREQUEST._serialized_end=230
  _COMMITVOTE._serialized_start=232
  _COMMITVOTE._serialized_end=296
  _TWONUMBERS._serialized_start=298
  _TWONUMBERS._serialized_end=332
  _SUM._serialized_start=334
  _SUM._serialized_end=352
  _SENDREQUEST._serialized_start=354
  _SENDREQUEST._serialized_end=419
  _SENDRESPONSE._serialized_start=421
  _SENDRESPONSE._serialized_end=469
  _CHATMESSAGE._serialized_start=471
  _CHATMESSAGE._serialized_end=517
  _USER._serialized_start=519
  _USER._serialized_end=543
  _LOGINREQUEST._serialized_start=545
  _LOGINREQUEST._serialized_end=595
  _LOGINRESPONSE._serialized_start=597
  _LOGINRESPONSE._serialized_end=646
  _REGISTERREQUEST._serialized_start=648
  _REGISTERREQUEST._serialized_end=701
  _REGISTERRESPONSE._serialized_start=703
  _REGISTERRESPONSE._serialized_end=755
  _DELETEREQUEST._serialized_start=757
  _DELETEREQUEST._serialized_end=790
  _DELETERESPONSE._serialized_start=792
  _DELETERESPONSE._serialized_end=842
  _CHATSERVICE._serialized_start=845
  _CHATSERVICE._serialized_end=1464
# @@protoc_insertion_point(module_scope)
