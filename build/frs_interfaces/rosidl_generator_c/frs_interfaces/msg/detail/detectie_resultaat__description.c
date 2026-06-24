// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from frs_interfaces:msg/DetectieResultaat.idl
// generated code does not contain a copyright notice

#include "frs_interfaces/msg/detail/detectie_resultaat__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_frs_interfaces
const rosidl_type_hash_t *
frs_interfaces__msg__DetectieResultaat__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0xd6, 0x9d, 0x52, 0x3d, 0xa7, 0xc0, 0xd2, 0xa5,
      0xc5, 0x1b, 0xfb, 0xa0, 0x76, 0xcd, 0xa2, 0x14,
      0xb9, 0xca, 0x52, 0x53, 0xa8, 0x2e, 0x17, 0x08,
      0xb2, 0xa4, 0xf6, 0x44, 0x0b, 0x41, 0x2a, 0x6f,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types

// Hashes for external referenced types
#ifndef NDEBUG
#endif

static char frs_interfaces__msg__DetectieResultaat__TYPE_NAME[] = "frs_interfaces/msg/DetectieResultaat";

// Define type names, field names, and default values
static char frs_interfaces__msg__DetectieResultaat__FIELD_NAME__klasse[] = "klasse";
static char frs_interfaces__msg__DetectieResultaat__FIELD_NAME__confidence[] = "confidence";
static char frs_interfaces__msg__DetectieResultaat__FIELD_NAME__x[] = "x";
static char frs_interfaces__msg__DetectieResultaat__FIELD_NAME__y[] = "y";
static char frs_interfaces__msg__DetectieResultaat__FIELD_NAME__z[] = "z";
static char frs_interfaces__msg__DetectieResultaat__FIELD_NAME__rotatie[] = "rotatie";

static rosidl_runtime_c__type_description__Field frs_interfaces__msg__DetectieResultaat__FIELDS[] = {
  {
    {frs_interfaces__msg__DetectieResultaat__FIELD_NAME__klasse, 6, 6},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_STRING,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {frs_interfaces__msg__DetectieResultaat__FIELD_NAME__confidence, 10, 10},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {frs_interfaces__msg__DetectieResultaat__FIELD_NAME__x, 1, 1},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {frs_interfaces__msg__DetectieResultaat__FIELD_NAME__y, 1, 1},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {frs_interfaces__msg__DetectieResultaat__FIELD_NAME__z, 1, 1},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {frs_interfaces__msg__DetectieResultaat__FIELD_NAME__rotatie, 7, 7},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
};

const rosidl_runtime_c__type_description__TypeDescription *
frs_interfaces__msg__DetectieResultaat__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {frs_interfaces__msg__DetectieResultaat__TYPE_NAME, 36, 36},
      {frs_interfaces__msg__DetectieResultaat__FIELDS, 6, 6},
    },
    {NULL, 0, 0},
  };
  if (!constructed) {
    constructed = true;
  }
  return &description;
}

static char toplevel_type_raw_source[] =
  "string klasse\n"
  "float32 confidence\n"
  "float32 x\n"
  "float32 y\n"
  "float32 z\n"
  "float32 rotatie";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
frs_interfaces__msg__DetectieResultaat__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {frs_interfaces__msg__DetectieResultaat__TYPE_NAME, 36, 36},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 79, 79},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
frs_interfaces__msg__DetectieResultaat__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[1];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 1, 1};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *frs_interfaces__msg__DetectieResultaat__get_individual_type_description_source(NULL),
    constructed = true;
  }
  return &source_sequence;
}
