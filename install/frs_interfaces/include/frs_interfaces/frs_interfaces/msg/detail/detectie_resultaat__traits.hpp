// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from frs_interfaces:msg/DetectieResultaat.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "frs_interfaces/msg/detectie_resultaat.hpp"


#ifndef FRS_INTERFACES__MSG__DETAIL__DETECTIE_RESULTAAT__TRAITS_HPP_
#define FRS_INTERFACES__MSG__DETAIL__DETECTIE_RESULTAAT__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "frs_interfaces/msg/detail/detectie_resultaat__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace frs_interfaces
{

namespace msg
{

inline void to_flow_style_yaml(
  const DetectieResultaat & msg,
  std::ostream & out)
{
  out << "{";
  // member: klasse
  {
    out << "klasse: ";
    rosidl_generator_traits::value_to_yaml(msg.klasse, out);
    out << ", ";
  }

  // member: confidence
  {
    out << "confidence: ";
    rosidl_generator_traits::value_to_yaml(msg.confidence, out);
    out << ", ";
  }

  // member: x
  {
    out << "x: ";
    rosidl_generator_traits::value_to_yaml(msg.x, out);
    out << ", ";
  }

  // member: y
  {
    out << "y: ";
    rosidl_generator_traits::value_to_yaml(msg.y, out);
    out << ", ";
  }

  // member: z
  {
    out << "z: ";
    rosidl_generator_traits::value_to_yaml(msg.z, out);
    out << ", ";
  }

  // member: rotatie
  {
    out << "rotatie: ";
    rosidl_generator_traits::value_to_yaml(msg.rotatie, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const DetectieResultaat & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: klasse
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "klasse: ";
    rosidl_generator_traits::value_to_yaml(msg.klasse, out);
    out << "\n";
  }

  // member: confidence
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "confidence: ";
    rosidl_generator_traits::value_to_yaml(msg.confidence, out);
    out << "\n";
  }

  // member: x
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "x: ";
    rosidl_generator_traits::value_to_yaml(msg.x, out);
    out << "\n";
  }

  // member: y
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "y: ";
    rosidl_generator_traits::value_to_yaml(msg.y, out);
    out << "\n";
  }

  // member: z
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "z: ";
    rosidl_generator_traits::value_to_yaml(msg.z, out);
    out << "\n";
  }

  // member: rotatie
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "rotatie: ";
    rosidl_generator_traits::value_to_yaml(msg.rotatie, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const DetectieResultaat & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace msg

}  // namespace frs_interfaces

namespace rosidl_generator_traits
{

[[deprecated("use frs_interfaces::msg::to_block_style_yaml() instead")]]
inline void to_yaml(
  const frs_interfaces::msg::DetectieResultaat & msg,
  std::ostream & out, size_t indentation = 0)
{
  frs_interfaces::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use frs_interfaces::msg::to_yaml() instead")]]
inline std::string to_yaml(const frs_interfaces::msg::DetectieResultaat & msg)
{
  return frs_interfaces::msg::to_yaml(msg);
}

template<>
inline const char * data_type<frs_interfaces::msg::DetectieResultaat>()
{
  return "frs_interfaces::msg::DetectieResultaat";
}

template<>
inline const char * name<frs_interfaces::msg::DetectieResultaat>()
{
  return "frs_interfaces/msg/DetectieResultaat";
}

template<>
struct has_fixed_size<frs_interfaces::msg::DetectieResultaat>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<frs_interfaces::msg::DetectieResultaat>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<frs_interfaces::msg::DetectieResultaat>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // FRS_INTERFACES__MSG__DETAIL__DETECTIE_RESULTAAT__TRAITS_HPP_
