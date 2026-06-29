// generated from rosidl_typesupport_fastrtps_c/resource/idl__rosidl_typesupport_fastrtps_c.h.em
// with input from frs_interfaces:msg/DetectieResultaat.idl
// generated code does not contain a copyright notice
#ifndef FRS_INTERFACES__MSG__DETAIL__DETECTIE_RESULTAAT__ROSIDL_TYPESUPPORT_FASTRTPS_C_H_
#define FRS_INTERFACES__MSG__DETAIL__DETECTIE_RESULTAAT__ROSIDL_TYPESUPPORT_FASTRTPS_C_H_


#include <stddef.h>
#include "rosidl_runtime_c/message_type_support_struct.h"
#include "rosidl_typesupport_interface/macros.h"
#include "frs_interfaces/msg/rosidl_typesupport_fastrtps_c__visibility_control.h"
#include "frs_interfaces/msg/detail/detectie_resultaat__struct.h"
#include "fastcdr/Cdr.h"

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_frs_interfaces
bool cdr_serialize_frs_interfaces__msg__DetectieResultaat(
  const frs_interfaces__msg__DetectieResultaat * ros_message,
  eprosima::fastcdr::Cdr & cdr);

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_frs_interfaces
bool cdr_deserialize_frs_interfaces__msg__DetectieResultaat(
  eprosima::fastcdr::Cdr &,
  frs_interfaces__msg__DetectieResultaat * ros_message);

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_frs_interfaces
size_t get_serialized_size_frs_interfaces__msg__DetectieResultaat(
  const void * untyped_ros_message,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_frs_interfaces
size_t max_serialized_size_frs_interfaces__msg__DetectieResultaat(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_frs_interfaces
bool cdr_serialize_key_frs_interfaces__msg__DetectieResultaat(
  const frs_interfaces__msg__DetectieResultaat * ros_message,
  eprosima::fastcdr::Cdr & cdr);

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_frs_interfaces
size_t get_serialized_size_key_frs_interfaces__msg__DetectieResultaat(
  const void * untyped_ros_message,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_frs_interfaces
size_t max_serialized_size_key_frs_interfaces__msg__DetectieResultaat(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_frs_interfaces
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, frs_interfaces, msg, DetectieResultaat)();

#ifdef __cplusplus
}
#endif

#endif  // FRS_INTERFACES__MSG__DETAIL__DETECTIE_RESULTAAT__ROSIDL_TYPESUPPORT_FASTRTPS_C_H_
