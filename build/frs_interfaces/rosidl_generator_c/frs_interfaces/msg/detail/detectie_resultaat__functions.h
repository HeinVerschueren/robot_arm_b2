// generated from rosidl_generator_c/resource/idl__functions.h.em
// with input from frs_interfaces:msg/DetectieResultaat.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "frs_interfaces/msg/detectie_resultaat.h"


#ifndef FRS_INTERFACES__MSG__DETAIL__DETECTIE_RESULTAAT__FUNCTIONS_H_
#define FRS_INTERFACES__MSG__DETAIL__DETECTIE_RESULTAAT__FUNCTIONS_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stdlib.h>

#include "rosidl_runtime_c/action_type_support_struct.h"
#include "rosidl_runtime_c/message_type_support_struct.h"
#include "rosidl_runtime_c/service_type_support_struct.h"
#include "rosidl_runtime_c/type_description/type_description__struct.h"
#include "rosidl_runtime_c/type_description/type_source__struct.h"
#include "rosidl_runtime_c/type_hash.h"
#include "rosidl_runtime_c/visibility_control.h"
#include "frs_interfaces/msg/rosidl_generator_c__visibility_control.h"

#include "frs_interfaces/msg/detail/detectie_resultaat__struct.h"

/// Initialize msg/DetectieResultaat message.
/**
 * If the init function is called twice for the same message without
 * calling fini inbetween previously allocated memory will be leaked.
 * \param[in,out] msg The previously allocated message pointer.
 * Fields without a default value will not be initialized by this function.
 * You might want to call memset(msg, 0, sizeof(
 * frs_interfaces__msg__DetectieResultaat
 * )) before or use
 * frs_interfaces__msg__DetectieResultaat__create()
 * to allocate and initialize the message.
 * \return true if initialization was successful, otherwise false
 */
ROSIDL_GENERATOR_C_PUBLIC_frs_interfaces
bool
frs_interfaces__msg__DetectieResultaat__init(frs_interfaces__msg__DetectieResultaat * msg);

/// Finalize msg/DetectieResultaat message.
/**
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_frs_interfaces
void
frs_interfaces__msg__DetectieResultaat__fini(frs_interfaces__msg__DetectieResultaat * msg);

/// Create msg/DetectieResultaat message.
/**
 * It allocates the memory for the message, sets the memory to zero, and
 * calls
 * frs_interfaces__msg__DetectieResultaat__init().
 * \return The pointer to the initialized message if successful,
 * otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_frs_interfaces
frs_interfaces__msg__DetectieResultaat *
frs_interfaces__msg__DetectieResultaat__create(void);

/// Destroy msg/DetectieResultaat message.
/**
 * It calls
 * frs_interfaces__msg__DetectieResultaat__fini()
 * and frees the memory of the message.
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_frs_interfaces
void
frs_interfaces__msg__DetectieResultaat__destroy(frs_interfaces__msg__DetectieResultaat * msg);

/// Check for msg/DetectieResultaat message equality.
/**
 * \param[in] lhs The message on the left hand size of the equality operator.
 * \param[in] rhs The message on the right hand size of the equality operator.
 * \return true if messages are equal, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_frs_interfaces
bool
frs_interfaces__msg__DetectieResultaat__are_equal(const frs_interfaces__msg__DetectieResultaat * lhs, const frs_interfaces__msg__DetectieResultaat * rhs);

/// Copy a msg/DetectieResultaat message.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source message pointer.
 * \param[out] output The target message pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer is null
 *   or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_frs_interfaces
bool
frs_interfaces__msg__DetectieResultaat__copy(
  const frs_interfaces__msg__DetectieResultaat * input,
  frs_interfaces__msg__DetectieResultaat * output);

/// Retrieve pointer to the hash of the description of this type.
ROSIDL_GENERATOR_C_PUBLIC_frs_interfaces
const rosidl_type_hash_t *
frs_interfaces__msg__DetectieResultaat__get_type_hash(
  const rosidl_message_type_support_t * type_support);

/// Retrieve pointer to the description of this type.
ROSIDL_GENERATOR_C_PUBLIC_frs_interfaces
const rosidl_runtime_c__type_description__TypeDescription *
frs_interfaces__msg__DetectieResultaat__get_type_description(
  const rosidl_message_type_support_t * type_support);

/// Retrieve pointer to the single raw source text that defined this type.
ROSIDL_GENERATOR_C_PUBLIC_frs_interfaces
const rosidl_runtime_c__type_description__TypeSource *
frs_interfaces__msg__DetectieResultaat__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support);

/// Retrieve pointer to the recursive raw sources that defined the description of this type.
ROSIDL_GENERATOR_C_PUBLIC_frs_interfaces
const rosidl_runtime_c__type_description__TypeSource__Sequence *
frs_interfaces__msg__DetectieResultaat__get_type_description_sources(
  const rosidl_message_type_support_t * type_support);

/// Initialize array of msg/DetectieResultaat messages.
/**
 * It allocates the memory for the number of elements and calls
 * frs_interfaces__msg__DetectieResultaat__init()
 * for each element of the array.
 * \param[in,out] array The allocated array pointer.
 * \param[in] size The size / capacity of the array.
 * \return true if initialization was successful, otherwise false
 * If the array pointer is valid and the size is zero it is guaranteed
 # to return true.
 */
ROSIDL_GENERATOR_C_PUBLIC_frs_interfaces
bool
frs_interfaces__msg__DetectieResultaat__Sequence__init(frs_interfaces__msg__DetectieResultaat__Sequence * array, size_t size);

/// Finalize array of msg/DetectieResultaat messages.
/**
 * It calls
 * frs_interfaces__msg__DetectieResultaat__fini()
 * for each element of the array and frees the memory for the number of
 * elements.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_frs_interfaces
void
frs_interfaces__msg__DetectieResultaat__Sequence__fini(frs_interfaces__msg__DetectieResultaat__Sequence * array);

/// Create array of msg/DetectieResultaat messages.
/**
 * It allocates the memory for the array and calls
 * frs_interfaces__msg__DetectieResultaat__Sequence__init().
 * \param[in] size The size / capacity of the array.
 * \return The pointer to the initialized array if successful, otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_frs_interfaces
frs_interfaces__msg__DetectieResultaat__Sequence *
frs_interfaces__msg__DetectieResultaat__Sequence__create(size_t size);

/// Destroy array of msg/DetectieResultaat messages.
/**
 * It calls
 * frs_interfaces__msg__DetectieResultaat__Sequence__fini()
 * on the array,
 * and frees the memory of the array.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_frs_interfaces
void
frs_interfaces__msg__DetectieResultaat__Sequence__destroy(frs_interfaces__msg__DetectieResultaat__Sequence * array);

/// Check for msg/DetectieResultaat message array equality.
/**
 * \param[in] lhs The message array on the left hand size of the equality operator.
 * \param[in] rhs The message array on the right hand size of the equality operator.
 * \return true if message arrays are equal in size and content, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_frs_interfaces
bool
frs_interfaces__msg__DetectieResultaat__Sequence__are_equal(const frs_interfaces__msg__DetectieResultaat__Sequence * lhs, const frs_interfaces__msg__DetectieResultaat__Sequence * rhs);

/// Copy an array of msg/DetectieResultaat messages.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source array pointer.
 * \param[out] output The target array pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer
 *   is null or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_frs_interfaces
bool
frs_interfaces__msg__DetectieResultaat__Sequence__copy(
  const frs_interfaces__msg__DetectieResultaat__Sequence * input,
  frs_interfaces__msg__DetectieResultaat__Sequence * output);

#ifdef __cplusplus
}
#endif

#endif  // FRS_INTERFACES__MSG__DETAIL__DETECTIE_RESULTAAT__FUNCTIONS_H_
