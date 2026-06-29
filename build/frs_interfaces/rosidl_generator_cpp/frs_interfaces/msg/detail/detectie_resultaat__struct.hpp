// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from frs_interfaces:msg/DetectieResultaat.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "frs_interfaces/msg/detectie_resultaat.hpp"


#ifndef FRS_INTERFACES__MSG__DETAIL__DETECTIE_RESULTAAT__STRUCT_HPP_
#define FRS_INTERFACES__MSG__DETAIL__DETECTIE_RESULTAAT__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__frs_interfaces__msg__DetectieResultaat __attribute__((deprecated))
#else
# define DEPRECATED__frs_interfaces__msg__DetectieResultaat __declspec(deprecated)
#endif

namespace frs_interfaces
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct DetectieResultaat_
{
  using Type = DetectieResultaat_<ContainerAllocator>;

  explicit DetectieResultaat_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->klasse = "";
      this->confidence = 0.0f;
      this->x = 0.0f;
      this->y = 0.0f;
      this->z = 0.0f;
      this->rotatie = 0.0f;
    }
  }

  explicit DetectieResultaat_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : klasse(_alloc)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->klasse = "";
      this->confidence = 0.0f;
      this->x = 0.0f;
      this->y = 0.0f;
      this->z = 0.0f;
      this->rotatie = 0.0f;
    }
  }

  // field types and members
  using _klasse_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _klasse_type klasse;
  using _confidence_type =
    float;
  _confidence_type confidence;
  using _x_type =
    float;
  _x_type x;
  using _y_type =
    float;
  _y_type y;
  using _z_type =
    float;
  _z_type z;
  using _rotatie_type =
    float;
  _rotatie_type rotatie;

  // setters for named parameter idiom
  Type & set__klasse(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->klasse = _arg;
    return *this;
  }
  Type & set__confidence(
    const float & _arg)
  {
    this->confidence = _arg;
    return *this;
  }
  Type & set__x(
    const float & _arg)
  {
    this->x = _arg;
    return *this;
  }
  Type & set__y(
    const float & _arg)
  {
    this->y = _arg;
    return *this;
  }
  Type & set__z(
    const float & _arg)
  {
    this->z = _arg;
    return *this;
  }
  Type & set__rotatie(
    const float & _arg)
  {
    this->rotatie = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    frs_interfaces::msg::DetectieResultaat_<ContainerAllocator> *;
  using ConstRawPtr =
    const frs_interfaces::msg::DetectieResultaat_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<frs_interfaces::msg::DetectieResultaat_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<frs_interfaces::msg::DetectieResultaat_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      frs_interfaces::msg::DetectieResultaat_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<frs_interfaces::msg::DetectieResultaat_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      frs_interfaces::msg::DetectieResultaat_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<frs_interfaces::msg::DetectieResultaat_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<frs_interfaces::msg::DetectieResultaat_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<frs_interfaces::msg::DetectieResultaat_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__frs_interfaces__msg__DetectieResultaat
    std::shared_ptr<frs_interfaces::msg::DetectieResultaat_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__frs_interfaces__msg__DetectieResultaat
    std::shared_ptr<frs_interfaces::msg::DetectieResultaat_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const DetectieResultaat_ & other) const
  {
    if (this->klasse != other.klasse) {
      return false;
    }
    if (this->confidence != other.confidence) {
      return false;
    }
    if (this->x != other.x) {
      return false;
    }
    if (this->y != other.y) {
      return false;
    }
    if (this->z != other.z) {
      return false;
    }
    if (this->rotatie != other.rotatie) {
      return false;
    }
    return true;
  }
  bool operator!=(const DetectieResultaat_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct DetectieResultaat_

// alias to use template instance with default allocator
using DetectieResultaat =
  frs_interfaces::msg::DetectieResultaat_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace frs_interfaces

#endif  // FRS_INTERFACES__MSG__DETAIL__DETECTIE_RESULTAAT__STRUCT_HPP_
