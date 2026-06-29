// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from frs_interfaces:msg/DetectieResultaat.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "frs_interfaces/msg/detail/detectie_resultaat__rosidl_typesupport_introspection_c.h"
#include "frs_interfaces/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "frs_interfaces/msg/detail/detectie_resultaat__functions.h"
#include "frs_interfaces/msg/detail/detectie_resultaat__struct.h"


// Include directives for member types
// Member `klasse`
#include "rosidl_runtime_c/string_functions.h"

#ifdef __cplusplus
extern "C"
{
#endif

void frs_interfaces__msg__DetectieResultaat__rosidl_typesupport_introspection_c__DetectieResultaat_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  frs_interfaces__msg__DetectieResultaat__init(message_memory);
}

void frs_interfaces__msg__DetectieResultaat__rosidl_typesupport_introspection_c__DetectieResultaat_fini_function(void * message_memory)
{
  frs_interfaces__msg__DetectieResultaat__fini(message_memory);
}

static rosidl_typesupport_introspection_c__MessageMember frs_interfaces__msg__DetectieResultaat__rosidl_typesupport_introspection_c__DetectieResultaat_message_member_array[6] = {
  {
    "klasse",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_STRING,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(frs_interfaces__msg__DetectieResultaat, klasse),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "confidence",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_FLOAT,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(frs_interfaces__msg__DetectieResultaat, confidence),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "x",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_FLOAT,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(frs_interfaces__msg__DetectieResultaat, x),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "y",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_FLOAT,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(frs_interfaces__msg__DetectieResultaat, y),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "z",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_FLOAT,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(frs_interfaces__msg__DetectieResultaat, z),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "rotatie",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_FLOAT,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(frs_interfaces__msg__DetectieResultaat, rotatie),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers frs_interfaces__msg__DetectieResultaat__rosidl_typesupport_introspection_c__DetectieResultaat_message_members = {
  "frs_interfaces__msg",  // message namespace
  "DetectieResultaat",  // message name
  6,  // number of fields
  sizeof(frs_interfaces__msg__DetectieResultaat),
  false,  // has_any_key_member_
  frs_interfaces__msg__DetectieResultaat__rosidl_typesupport_introspection_c__DetectieResultaat_message_member_array,  // message members
  frs_interfaces__msg__DetectieResultaat__rosidl_typesupport_introspection_c__DetectieResultaat_init_function,  // function to initialize message memory (memory has to be allocated)
  frs_interfaces__msg__DetectieResultaat__rosidl_typesupport_introspection_c__DetectieResultaat_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t frs_interfaces__msg__DetectieResultaat__rosidl_typesupport_introspection_c__DetectieResultaat_message_type_support_handle = {
  0,
  &frs_interfaces__msg__DetectieResultaat__rosidl_typesupport_introspection_c__DetectieResultaat_message_members,
  get_message_typesupport_handle_function,
  &frs_interfaces__msg__DetectieResultaat__get_type_hash,
  &frs_interfaces__msg__DetectieResultaat__get_type_description,
  &frs_interfaces__msg__DetectieResultaat__get_type_description_sources,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_frs_interfaces
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, frs_interfaces, msg, DetectieResultaat)() {
  if (!frs_interfaces__msg__DetectieResultaat__rosidl_typesupport_introspection_c__DetectieResultaat_message_type_support_handle.typesupport_identifier) {
    frs_interfaces__msg__DetectieResultaat__rosidl_typesupport_introspection_c__DetectieResultaat_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &frs_interfaces__msg__DetectieResultaat__rosidl_typesupport_introspection_c__DetectieResultaat_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif
