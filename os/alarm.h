#ifndef __OS_KRN_ALARM_H__
#define __OS_KRN_ALARM_H__

#include "stdint.h"
#include "counter.h"
#include "util/inline.h"
#include "scheduler/task.h"

using namespace os::scheduler;

namespace os {

class Alarm {
public:
	inlinehint static void checkCounter(const Counter& counter);
};

template<const UnencodedCounter* const configuration_>
class UnencodedAlarm : public Alarm {
	typedef UnencodedCounter CounterType;

	bool armed_;
	TickType absoluteTime_;
	TickType cycleTime_;
public:
	/** \brief task to activate */
	const Task* const task_;
    const uint32_t id_;

	constexpr UnencodedAlarm(const uint32_t id) : armed_(false), absoluteTime_(0), cycleTime_(0), task_(0), id_(id) {}
	constexpr UnencodedAlarm(const Task& task, const uint32_t id) : armed_(false), absoluteTime_(0), cycleTime_(0), task_(&task), id_(id) {}
	constexpr UnencodedAlarm(const Task& task, bool armed, TickType absoluteTime, TickType cycleTime, const uint32_t id) :
		armed_(armed), absoluteTime_(absoluteTime), cycleTime_(cycleTime), task_(&task), id_(id) {}

	void setArmed (bool armed) {
		armed_ = armed;
	}

	bool getArmed () const {
		return armed_;
	}

	void setAbsoluteTime (TickType absoluteTime) {
		absoluteTime_ = absoluteTime;
	}

	template<typename Encoded>
	void setRelativeTime(Encoded encoded) {
		setRelativeTime(encoded.decode());
	}

	void setRelativeTime(TickType relativeTime) {
		auto value = configuration_->getValue();
		auto remaining = configuration_->maxallowedvalue - value;

		if((relativeTime <= remaining) == 1) {
			absoluteTime_ = value + relativeTime;
		} else {
			absoluteTime_ = relativeTime - remaining - 1;
		}
	}

	TickType getAbsoluteTime () const {
		return absoluteTime_;
	}

	template<typename Encoded>
	void setCycleTime(Encoded encoded) {
		setCycleTime(encoded.decode());
	}

	void setCycleTime (TickType cycleTime) {
		cycleTime_ = cycleTime;
	}

	TickType getCycleTime () const {
		return cycleTime_;
	}

	TickType getRemainingTicks() {
		auto abstime = getAbsoluteTime();
		auto counter = configuration_->getValue();

		if( (abstime <= counter) == 1) {
			return abstime + (configuration_->maxallowedvalue - counter);
		} else {
			return abstime - counter;
		}
	}

	forceinline bool checkTrigger() {
		if((getArmed() == 1) && (getAbsoluteTime() == configuration_->getValue())) {
			auto cycletime = getCycleTime();
			if(cycletime != 0) {
				// reconfigure cyclic alarm
				setRelativeTime(cycletime);
			} else {
				// disable single shot
				setArmed(false);
			}
			return true;
		}
		return false; // was false!
	}

};

template<B_t B, B_t CB, const EncodedCounter<CB>* const configuration_>
class EncodedAlarm : public Alarm {
	typedef EncodedCounter<CB> CounterType;

	Encoded_Static<A0, B> armed_;
	Encoded_Static<A0, B+5> absoluteTime_;
	Encoded_Static<A0, B+3> cycleTime_;

public:
	/** \brief task to activate */
	const Task* const task_;
    const uint32_t id_;

	constexpr EncodedAlarm(const uint32_t id) : armed_(false), absoluteTime_(0), cycleTime_(0), task_(0), id_(id) {}
	constexpr EncodedAlarm(const Task& task, const uint32_t id) : armed_(false), absoluteTime_(0), cycleTime_(0), task_(&task), id_(id) {}
	constexpr EncodedAlarm(const Task& task, bool armed, TickType absoluteTime, TickType cycleTime, const uint32_t id) :
		armed_(armed), absoluteTime_(absoluteTime), cycleTime_(cycleTime), task_(&task), id_(id) {}

	template<typename Encoded>
	void setArmed(Encoded encoded) {
		armed_ = encoded;
	}

	void setArmed (bool armed) {
		armed_.encode(armed);
	}

	decltype(armed_) getArmed () const {
		armed_.check();
		return armed_;
	}

	void setAbsoluteTime (TickType absoluteTime) {
		absoluteTime_.encode(absoluteTime);
	}

	template<typename Encoded>
	void setRelativeTime(Encoded relativeTime) {
		auto value = configuration_->getValue();
		auto remaining = configuration_->maxallowedvalue - value;

		if((relativeTime <= Encoded_Static<A0, Encoded::B+6>(remaining)) == 1) {
			absoluteTime_ = value + relativeTime;
		} else {
			absoluteTime_ = relativeTime - remaining - EC(B, 1);
		}
	}

	decltype(absoluteTime_) getAbsoluteTime () const {
		absoluteTime_.check();
		return absoluteTime_;
	}

	template<typename Encoded>
	void setCycleTime(Encoded encoded) {
		cycleTime_ = encoded;
	}

	void setCycleTime (TickType cycleTime) {
		cycleTime_.encode(cycleTime);
	}

	decltype(cycleTime_) getCycleTime () const {
		cycleTime_.check();
		return cycleTime_;
	}

	TickType getRemainingTicks() {
		auto abstime = getAbsoluteTime();
		auto counter = configuration_->getValue();

		if( (abstime <= Encoded_Static<A0, decltype(abstime)::B+6>(counter)) == 1) {
			auto ret = abstime + (configuration_->maxallowedvalue - counter);
			return ret.decode();
		} else {
			auto ret = abstime - counter;
			return ret.decode();
		}
	}

	forceinline bool checkTrigger() {
		if((getArmed() == 1) && (getAbsoluteTime() == configuration_->getValue())) {
			auto cycletime = getCycleTime();
			if(cycletime != 0) {
				// reconfigure cyclic alarm
				setRelativeTime(cycletime);
			} else {
				// disable single shot
				setArmed(EC(B+2, 0));
			}
			return true;
		}
		return false;
	}
};


} // namespace os

#endif // __OS_KRN_ALARM_H__
