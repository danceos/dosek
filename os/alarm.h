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
	typedef uint32_t Ticks;

	const Counter& configuration_;

	bool armed_;
	Ticks absoluteTime_;
	Ticks cycleTime_;

public:
	/** \brief task to activate */
	const Task* const task_;

	constexpr Alarm(Counter& counter) : configuration_(counter), armed_(false), absoluteTime_(0), cycleTime_(0), task_(0) {}
	constexpr Alarm(Counter& counter, const Task& task) : configuration_(counter), armed_(false),
														  absoluteTime_(0), cycleTime_(0), task_(&task) {}
	constexpr Alarm(Counter& counter, const Task& task, bool armed, 
					Ticks absoluteTime, Ticks cycleTime) : 
		configuration_(counter), armed_(armed),
		absoluteTime_(absoluteTime), cycleTime_(cycleTime), task_(&task) {}


	void setArmed (bool armed) {
		armed_ = armed;
	}

	bool getArmed () {
		return armed_;
	}

	void setAbsoluteTime (Ticks absoluteTime) {
		absoluteTime_ = absoluteTime;
	}

	void setRelativeTime (Ticks relativeTime) {
		Ticks remaining = configuration_.maxallowedvalue - configuration_.getValue();

		if(remaining >= relativeTime) {
			absoluteTime_ = configuration_.getValue() + relativeTime;
		} else {
			absoluteTime_ = relativeTime - remaining - 1;
		}
	}

	Ticks getAbsoluteTime () {
		return absoluteTime_;
	}

	void setCycleTime (Ticks cycleTime) {
		cycleTime_ = cycleTime;
	}

	Ticks getCycleTime () {
		return cycleTime_;
	}

	Ticks getRemainingTicks() {
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
