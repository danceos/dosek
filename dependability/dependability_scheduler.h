
#ifndef _COREDOS_OS_DEPENDABILITY_SCHEDULER_H_
#define _COREDOS_OS_DEPENDABILITY_SCHEDULER_H_

namespace dep {
	class Dependability_Scheduler
	{
	public:

		enum Object_State {
			FAILURE,      ///< The checksum calculation was interrupted by a task
			SUCCESS,      ///< The checksum calculation was successfull
		};

		/**
		 * \brief Constructs an empty storage.
		**/
		Dependability_Scheduler();

		/**
		 * \brief Returns the index of the next Checked_Object to check
		**/
		unsigned int get_next();

		/**
		 * \brief Report a complete checksum calculation
		 *
		 * \param index The CheckedObject that was checked
		 * \param state Whether the checksum calculation was interrupted or not
		**/
		void update(unsigned int index, enum Object_State state);

	private:
		unsigned int current;
	};
}

#endif
