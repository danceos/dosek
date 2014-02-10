#ifndef __OS_KRN_ALARM_H__
#define __OS_KRN_ALARM_H__

#include "stdint.h"
#include "counter.h"
#include "util/inline.h"
#include "scheduler/task.h"

using namespace os::scheduler;

namespace os {

class Counter;

class Alarm {
	const Counter& configuration_;

	bool armed_;
	TickType absoluteTime_;
	TickType cycleTime_;

public:
	/** \brief task to activate */
	const Task* const task_;

	constexpr Alarm(Counter& counter) : configuration_(counter), armed_(false), absoluteTime_(0), cycleTime_(0), task_(0) {}
	constexpr Alarm(Counter& counter, const Task& task) : configuration_(counter), armed_(false),
														  absoluteTime_(0), cycleTime_(0), task_(&task) {}
	constexpr Alarm(Counter& counter, const Task& task, bool armed, 
					TickType absoluteTime, TickType cycleTime) : 
		configuration_(counter), armed_(armed),
		absoluteTime_(absoluteTime), cycleTime_(cycleTime), task_(&task) {}


	void setArmed (bool armed) {
		armed_ = armed;
	}

	bool getArmed () {
		return armed_;
	}

	void setAbsoluteTime (TickType absoluteTime) {
		absoluteTime_ = absoluteTime;
	}

	template<typename Encoded>
	void setRelativeTime(Encoded encoded) {
		setRelativeTime(encoded.decode());
	}

	void setRelativeTime (TickType relativeTime) {
		TickType remaining = configuration_.maxallowedvalue - configuration_.getValue();

		if(remaining >= relativeTime) {
			absoluteTime_ = configuration_.getValue() + relativeTime;
		} else {
			absoluteTime_ = relativeTime - remaining - 1;
		}
	}

	TickType getAbsoluteTime () {
		return absoluteTime_;
	}

	template<typename Encoded>
	void setCycleTime(Encoded encoded) {
		setCycleTime(encoded.decode());
	}

	void setCycleTime (TickType cycleTime) {
		cycleTime_ = cycleTime;
	}

	TickType getCycleTime () {
		return cycleTime_;
	}

	TickType getRemainingTickType() {
		if(absoluteTime_ > configuration_.getValue()) {
			return absoluteTime_ - configuration_.getValue();
		} else {
			return absoluteTime_ + (configuration_.maxallowedvalue - configuration_.getValue());
		}
	}

	forceinline bool checkTrigger(const Counter* counter) {
		if(getArmed() && (&configuration_ == counter) && getAbsoluteTime() == counter->getValue()) {
			if(getCycleTime() > 0) {
				// reconfigure cyclic alarm
				setRelativeTime(getCycleTime());
			} else {
				// disable single shot
				setArmed(false);
			}
			return true;
		}
		return false;
	}

	static void checkCounter(const Counter& counter);
};

} // namespace os

#endif // __OS_KRN_ALARM_H__
