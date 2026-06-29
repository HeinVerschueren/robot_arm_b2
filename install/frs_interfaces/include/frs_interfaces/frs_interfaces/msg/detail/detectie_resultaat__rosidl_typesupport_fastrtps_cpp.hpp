// generated from rosidl_typesupport_fastrtps_cpp/resource/idl__rosidl_typesupport_fastrtps_cpp.hpp.em
// with input from frs_interfaces:msg/DetectieResultaat.idl
// generated code does not contain a copyright notice

#ifndef FRS_INTERFACES__MSG__DETAIL__DETECTIE_RESULTAAT__ROSIDL_TYPESUPPORT_FASTRTPS_CPP_HPP_
#define FRS_INTERFACES__MSG__DETAIL__DETECTIE_RESULTAAT__ROSIDL_TYPESUPPORT_FASTRTPS_CPP_HPP_

#include <cstddef>
#include "rosidl_runtime_c/message_type_support_struct.h"
#include "rosidl_typesupport_interface/macros.h"
#include "frs_interfaces/msg/rosidl_typesupport_fastrtps_cpp__visibility_control.h"
#include "frs_interfaces/msg/detail/detectie_resultaat__struct.hpp"

#ifndef _WIN32
# pragma GCC diagnostic push
# pragma GCC diagnostic ignored "-Wunused-parameter"
# ifdef __clang__
#  pragma clang diagnostic ignored "-Wdeprecated-register"
#  pragma clang diagnostic ignored "-Wreturn-type-c-linkage"
# endif
#endif
#ifndef _WIN32
# pragma GCC diagnostic pop
#endif

#include "fastcdr/Cdr.h"

namespace frs_interfaces
{

namespace msg
{

namespace typesupport_fastrtps_cpp
{

bool
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_frs_interfaces
cdr_serialize(
  const frs_interfaces::msg::DetectieResultaat & ros_message,
  eprosima::fastcdr::Cdr & cdr);

bool
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_frs_interfaces
cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  frs_interfaces::msg::DetectieResultaat & ros_message);

size_t
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_frs_interfaces
get_serialized_size(
  const frs_interfaces::msg::DetectieResultaat & ros_message,
  size_t current_alignment);

size_t
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_frs_interfaces
max_serialized_size_DetectieResultaat(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);

bool
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_frs_interfaces
cdr_serialize_key(
  const frs_interfaces::msg::DetectieResultaat & ros_message,
  eprosima::fastcdr::Cdr &);

size_t
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_frs_interfaces
get_serialized_size_key(
  const frs_interfaces::msg::DetectieResultaat & ros_message,
  size_t current_alignment);

size_t
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_frs_interfaces
max_serialized_size_key_DetectieResultaat(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);

}  // namespace typesupport_fastrtps_cpp

}  // namespace msg

}  // namespace frs_interfaces

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_frs_interfaces
const rosidl_message_type_support_t *
  ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_cpp, frs_interfaces, msg, DetectieResultaat)();

#ifdef __cplusplus
}
#endif

#endif  // FRS_INTERFACES__MSG__DETAIL__DETECTIE_RESULTAAT__ROSIDL_TYPESUPPORT_FASTRTPS_CPP_HPP_
