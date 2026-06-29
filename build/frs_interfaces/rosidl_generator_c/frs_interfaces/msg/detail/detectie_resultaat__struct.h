// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from frs_interfaces:msg/DetectieResultaat.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "frs_interfaces/msg/detectie_resultaat.h"


#ifndef FRS_INTERFACES__MSG__DETAIL__DETECTIE_RESULTAAT__STRUCT_H_
#define FRS_INTERFACES__MSG__DETAIL__DETECTIE_RESULTAAT__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

// Constants defined in the message

// Include directives for member types
// Member 'klasse'
#include "rosidl_runtime_c/string.h"

/// Struct defined in msg/DetectieResultaat in the package frs_interfaces.
typedef struct frs_interfaces__msg__DetectieResultaat
{
  rosidl_runtime_c__String klasse;
  float confidence;
  float x;
  float y;
  float z;
  float rotatie;
} frs_interfaces__msg__DetectieResultaat;

// Struct for a sequence of frs_interfaces__msg__DetectieResultaat.
typedef struct frs_interfaces__msg__DetectieResultaat__Sequence
{
  frs_interfaces__msg__DetectieResultaat * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} frs_interfaces__msg__DetectieResultaat__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // FRS_INTERFACES__MSG__DETAIL__DETECTIE_RESULTAAT__STRUCT_H_
