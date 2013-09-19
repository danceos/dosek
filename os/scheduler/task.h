#ifndef __TASK_H__
#define __TASK_H__

/* Simple task class */
class Task {
public:
	typedef uint8_t ID;
	typedef uint8_t Prio;

protected:
	union {
		struct {
			ID id;
			Prio prio;

		} fields;
		uint16_t combined;
	};

public:
	Task() : combined(0) {}

	Task(uint16_t comb) : combined(comb) {};

	Task(ID tid, Prio p) {
		fields.id = tid;
		fields.prio = p;
	} 

	ID getID() const {
		return fields.id;
	}

	Prio getPrio() const {
		return fields.prio;
	}

	uint16_t getCombined() const {
		return combined;
	}

	void setPrio(Prio newprio) {
		fields.prio = newprio;
	}
};

typedef Task::ID TaskID;
typedef Task::Prio TaskPrio;
static const Task INVALID_TASK = Task(0,0);
static const TaskID INVALID_TASK_ID = 0;

#endif // __TASK_H__
