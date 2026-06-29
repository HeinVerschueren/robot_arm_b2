// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from frs_interfaces:msg/DetectieResultaat.idl
// generated code does not contain a copyright notice
#include "frs_interfaces/msg/detail/detectie_resultaat__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `klasse`
#include "rosidl_runtime_c/string_functions.h"

bool
frs_interfaces__msg__DetectieResultaat__init(frs_interfaces__msg__DetectieResultaat * msg)
{
  if (!msg) {
    return false;
  }
  // klasse
  if (!rosidl_runtime_c__String__init(&msg->klasse)) {
    frs_interfaces__msg__DetectieResultaat__fini(msg);
    return false;
  }
  // confidence
  // x
  // y
  // z
  // rotatie
  return true;
}

void
frs_interfaces__msg__DetectieResultaat__fini(frs_interfaces__msg__DetectieResultaat * msg)
{
  if (!msg) {
    return;
  }
  // klasse
  rosidl_runtime_c__String__fini(&msg->klasse);
  // confidence
  // x
  // y
  // z
  // rotatie
}

bool
frs_interfaces__msg__DetectieResultaat__are_equal(const frs_interfaces__msg__DetectieResultaat * lhs, const frs_interfaces__msg__DetectieResultaat * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // klasse
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->klasse), &(rhs->klasse)))
  {
    return false;
  }
  // confidence
  if (lhs->confidence != rhs->confidence) {
    return false;
  }
  // x
  if (lhs->x != rhs->x) {
    return false;
  }
  // y
  if (lhs->y != rhs->y) {
    return false;
  }
  // z
  if (lhs->z != rhs->z) {
    return false;
  }
  // rotatie
  if (lhs->rotatie != rhs->rotatie) {
    return false;
  }
  return true;
}

bool
frs_interfaces__msg__DetectieResultaat__copy(
  const frs_interfaces__msg__DetectieResultaat * input,
  frs_interfaces__msg__DetectieResultaat * output)
{
  if (!input || !output) {
    return false;
  }
  // klasse
  if (!rosidl_runtime_c__String__copy(
      &(input->klasse), &(output->klasse)))
  {
    return false;
  }
  // confidence
  output->confidence = input->confidence;
  // x
  output->x = input->x;
  // y
  output->y = input->y;
  // z
  output->z = input->z;
  // rotatie
  output->rotatie = input->rotatie;
  return true;
}

frs_interfaces__msg__DetectieResultaat *
frs_interfaces__msg__DetectieResultaat__create(void)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  frs_interfaces__msg__DetectieResultaat * msg = (frs_interfaces__msg__DetectieResultaat *)allocator.allocate(sizeof(frs_interfaces__msg__DetectieResultaat), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(frs_interfaces__msg__DetectieResultaat));
  bool success = frs_interfaces__msg__DetectieResultaat__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
frs_interfaces__msg__DetectieResultaat__destroy(frs_interfaces__msg__DetectieResultaat * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    frs_interfaces__msg__DetectieResultaat__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
frs_interfaces__msg__DetectieResultaat__Sequence__init(frs_interfaces__msg__DetectieResultaat__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  frs_interfaces__msg__DetectieResultaat * data = NULL;

  if (size) {
    data = (frs_interfaces__msg__DetectieResultaat *)allocator.zero_allocate(size, sizeof(frs_interfaces__msg__DetectieResultaat), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = frs_interfaces__msg__DetectieResultaat__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        frs_interfaces__msg__DetectieResultaat__fini(&data[i - 1]);
      }
      allocator.deallocate(data, allocator.state);
      return false;
    }
  }
  array->data = data;
  array->size = size;
  array->capacity = size;
  return true;
}

void
frs_interfaces__msg__DetectieResultaat__Sequence__fini(frs_interfaces__msg__DetectieResultaat__Sequence * array)
{
  if (!array) {
    return;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();

  if (array->data) {
    // ensure that data and capacity values are consistent
    assert(array->capacity > 0);
    // finalize all array elements
    for (size_t i = 0; i < array->capacity; ++i) {
      frs_interfaces__msg__DetectieResultaat__fini(&array->data[i]);
    }
    allocator.deallocate(array->data, allocator.state);
    array->data = NULL;
    array->size = 0;
    array->capacity = 0;
  } else {
    // ensure that data, size, and capacity values are consistent
    assert(0 == array->size);
    assert(0 == array->capacity);
  }
}

frs_interfaces__msg__DetectieResultaat__Sequence *
frs_interfaces__msg__DetectieResultaat__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  frs_interfaces__msg__DetectieResultaat__Sequence * array = (frs_interfaces__msg__DetectieResultaat__Sequence *)allocator.allocate(sizeof(frs_interfaces__msg__DetectieResultaat__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = frs_interfaces__msg__DetectieResultaat__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
frs_interfaces__msg__DetectieResultaat__Sequence__destroy(frs_interfaces__msg__DetectieResultaat__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    frs_interfaces__msg__DetectieResultaat__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
frs_interfaces__msg__DetectieResultaat__Sequence__are_equal(const frs_interfaces__msg__DetectieResultaat__Sequence * lhs, const frs_interfaces__msg__DetectieResultaat__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!frs_interfaces__msg__DetectieResultaat__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
frs_interfaces__msg__DetectieResultaat__Sequence__copy(
  const frs_interfaces__msg__DetectieResultaat__Sequence * input,
  frs_interfaces__msg__DetectieResultaat__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(frs_interfaces__msg__DetectieResultaat);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    frs_interfaces__msg__DetectieResultaat * data =
      (frs_interfaces__msg__DetectieResultaat *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!frs_interfaces__msg__DetectieResultaat__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          frs_interfaces__msg__DetectieResultaat__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!frs_interfaces__msg__DetectieResultaat__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
