// generated from rosidl_typesupport_c/resource/idl__type_support.cpp.em
// with input from frs_interfaces:msg/DetectieResultaat.idl
// generated code does not contain a copyright notice

#include "cstddef"
#include "rosidl_runtime_c/message_type_support_struct.h"
#include "frs_interfaces/msg/detail/detectie_resultaat__struct.h"
#include "frs_interfaces/msg/detail/detectie_resultaat__type_support.h"
#include "frs_interfaces/msg/detail/detectie_resultaat__functions.h"
#include "rosidl_typesupport_c/identifier.h"
#include "rosidl_typesupport_c/message_type_support_dispatch.h"
#include "rosidl_typesupport_c/type_support_map.h"
#include "rosidl_typesupport_c/visibility_control.h"
#include "rosidl_typesupport_interface/macros.h"

namespace frs_interfaces
{

namespace msg
{

namespace rosidl_typesupport_c
{

typedef struct _DetectieResultaat_type_support_ids_t
{
  const char * typesupport_identifier[2];
} _DetectieResultaat_type_support_ids_t;

static const _DetectieResultaat_type_support_ids_t _DetectieResultaat_message_typesupport_ids = {
  {
    "rosidl_typesupport_fastrtps_c",  // ::rosidl_typesupport_fastrtps_c::typesupport_identifier,
    "rosidl_typesupport_introspection_c",  // ::rosidl_typesupport_introspection_c::typesupport_identifier,
  }
};

typedef struct _DetectieResultaat_type_support_symbol_names_t
{
  const char * symbol_name[2];
} _DetectieResultaat_type_support_symbol_names_t;

#define STRINGIFY_(s) #s
#define STRINGIFY(s) STRINGIFY_(s)

static const _DetectieResultaat_type_support_symbol_names_t _DetectieResultaat_message_typesupport_symbol_names = {
  {
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, frs_interfaces, msg, DetectieResultaat)),
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, frs_interfaces, msg, DetectieResultaat)),
  }
};

typedef struct _DetectieResultaat_type_support_data_t
{
  void * data[2];
} _DetectieResultaat_type_support_data_t;

static _DetectieResultaat_type_support_data_t _DetectieResultaat_message_typesupport_data = {
  {
    0,  // will store the shared library later
    0,  // will store the shared library later
  }
};

static const type_support_map_t _DetectieResultaat_message_typesupport_map = {
  2,
  "frs_interfaces",
  &_DetectieResultaat_message_typesupport_ids.typesupport_identifier[0],
  &_DetectieResultaat_message_typesupport_symbol_names.symbol_name[0],
  &_DetectieResultaat_message_typesupport_data.data[0],
};

static const rosidl_message_type_support_t DetectieResultaat_message_type_support_handle = {
  rosidl_typesupport_c__typesupport_identifier,
  reinterpret_cast<const type_support_map_t *>(&_DetectieResultaat_message_typesupport_map),
  rosidl_typesupport_c__get_message_typesupport_handle_function,
  &frs_interfaces__msg__DetectieResultaat__get_type_hash,
  &frs_interfaces__msg__DetectieResultaat__get_type_description,
  &frs_interfaces__msg__DetectieResultaat__get_type_description_sources,
};

}  // namespace rosidl_typesupport_c

}  // namespace msg

}  // namespace frs_interfaces

#ifdef __cplusplus
extern "C"
{
#endif

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_c, frs_interfaces, msg, DetectieResultaat)() {
  return &::frs_interfaces::msg::rosidl_typesupport_c::DetectieResultaat_message_type_support_handle;
}

#ifdef __cplusplus
}
#endif
