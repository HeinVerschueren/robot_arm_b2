// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from frs_interfaces:msg/DetectieResultaat.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "frs_interfaces/msg/detectie_resultaat.hpp"


#ifndef FRS_INTERFACES__MSG__DETAIL__DETECTIE_RESULTAAT__BUILDER_HPP_
#define FRS_INTERFACES__MSG__DETAIL__DETECTIE_RESULTAAT__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "frs_interfaces/msg/detail/detectie_resultaat__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace frs_interfaces
{

namespace msg
{

namespace builder
{

class Init_DetectieResultaat_rotatie
{
public:
  explicit Init_DetectieResultaat_rotatie(::frs_interfaces::msg::DetectieResultaat & msg)
  : msg_(msg)
  {}
  ::frs_interfaces::msg::DetectieResultaat rotatie(::frs_interfaces::msg::DetectieResultaat::_rotatie_type arg)
  {
    msg_.rotatie = std::move(arg);
    return std::move(msg_);
  }

private:
  ::frs_interfaces::msg::DetectieResultaat msg_;
};

class Init_DetectieResultaat_z
{
public:
  explicit Init_DetectieResultaat_z(::frs_interfaces::msg::DetectieResultaat & msg)
  : msg_(msg)
  {}
  Init_DetectieResultaat_rotatie z(::frs_interfaces::msg::DetectieResultaat::_z_type arg)
  {
    msg_.z = std::move(arg);
    return Init_DetectieResultaat_rotatie(msg_);
  }

private:
  ::frs_interfaces::msg::DetectieResultaat msg_;
};

class Init_DetectieResultaat_y
{
public:
  explicit Init_DetectieResultaat_y(::frs_interfaces::msg::DetectieResultaat & msg)
  : msg_(msg)
  {}
  Init_DetectieResultaat_z y(::frs_interfaces::msg::DetectieResultaat::_y_type arg)
  {
    msg_.y = std::move(arg);
    return Init_DetectieResultaat_z(msg_);
  }

private:
  ::frs_interfaces::msg::DetectieResultaat msg_;
};

class Init_DetectieResultaat_x
{
public:
  explicit Init_DetectieResultaat_x(::frs_interfaces::msg::DetectieResultaat & msg)
  : msg_(msg)
  {}
  Init_DetectieResultaat_y x(::frs_interfaces::msg::DetectieResultaat::_x_type arg)
  {
    msg_.x = std::move(arg);
    return Init_DetectieResultaat_y(msg_);
  }

private:
  ::frs_interfaces::msg::DetectieResultaat msg_;
};

class Init_DetectieResultaat_confidence
{
public:
  explicit Init_DetectieResultaat_confidence(::frs_interfaces::msg::DetectieResultaat & msg)
  : msg_(msg)
  {}
  Init_DetectieResultaat_x confidence(::frs_interfaces::msg::DetectieResultaat::_confidence_type arg)
  {
    msg_.confidence = std::move(arg);
    return Init_DetectieResultaat_x(msg_);
  }

private:
  ::frs_interfaces::msg::DetectieResultaat msg_;
};

class Init_DetectieResultaat_klasse
{
public:
  Init_DetectieResultaat_klasse()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_DetectieResultaat_confidence klasse(::frs_interfaces::msg::DetectieResultaat::_klasse_type arg)
  {
    msg_.klasse = std::move(arg);
    return Init_DetectieResultaat_confidence(msg_);
  }

private:
  ::frs_interfaces::msg::DetectieResultaat msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::frs_interfaces::msg::DetectieResultaat>()
{
  return frs_interfaces::msg::builder::Init_DetectieResultaat_klasse();
}

}  // namespace frs_interfaces

#endif  // FRS_INTERFACES__MSG__DETAIL__DETECTIE_RESULTAAT__BUILDER_HPP_
