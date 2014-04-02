#ifndef ENCODED_H_
#define ENCODED_H_

/**
 * @file
 * @ingroup os
 * @brief The EAN Encoding Data Type
 */

#include <stdint.h>
#include "assert.h"

#ifdef UINT16_MAX
#undef UINT16_MAX
#endif

#ifdef UINT32_MAX
#undef UINT32_MAX
#endif

#define UINT16_MAX 0xffffU
#define UINT32_MAX 0xffffffffU


#define __NUM_PRIMES 6542
#define __V_MAX UINT16_MAX
#define __VC_MAX UINT32_MAX

// Types
typedef uint32_t value_coded_t;
typedef uint16_t value_t;
typedef value_t A_t;
typedef uint16_t B_t;
typedef uint8_t D_t;

static const A_t superAs[5] = {58659, 59665, 63157, 63859, 63877};

// the one A we use for now
static const A_t A0 = 58659;

class Encoded
{
public:
	static value_coded_t encode(value_t v, A_t A, B_t B, D_t D) {
		return static_cast<value_coded_t>((A*v) + B + D);
	};

	static value_t decode(value_coded_t vc, A_t A, B_t B, D_t D) {
		assert(check(vc, A, B, D));
		return static_cast<value_t>((vc - B - D) / A);
	};

	static bool check(value_coded_t vc, A_t A, B_t B, D_t D)
	{
		bool nooverflow = vc < static_cast<value_coded_t>((__V_MAX * A) + B + D);
		bool noremainder = (((vc - B - D) % A) == 0);

		return  (nooverflow && noremainder);
	};
};

template<A_t _A, B_t _B>
class Encoded_Static : Encoded
{
public:
	value_coded_t vc;
	static const value_coded_t max_vc = static_cast<value_coded_t>((_A * __V_MAX) + _B);

	static const uint32_t MAXMODA = (__VC_MAX + 1ULL) % _A;

	static const A_t A = _A;
	static const B_t B = _B;

	static_assert(_B > 0, "static signature B must be > 0"); // not strictly necessary
	static_assert(_A > _B, "static signature B too large (bigger than A)");

	constexpr Encoded_Static() {};

	// implicit conversion constructor
	template<B_t TB>
	constexpr Encoded_Static(const Encoded_Static<_A, TB> &rhs) : vc(rhs.vc + (B - TB)) {};

	constexpr Encoded_Static(value_t value) : vc(static_cast<value_coded_t>(value * _A) + _B) {};

	bool check() const
	{
		bool nooverflow = vc < static_cast<value_coded_t>((__V_MAX * _A) + _B + getD());
		bool noremainder = (((vc - _B - getD()) % _A) == 0);

		return  (nooverflow && noremainder);
	};

	bool check() const volatile
	{
		bool nooverflow = vc < static_cast<value_coded_t>((__V_MAX * _A) + _B + getD());
		bool noremainder = (((vc - _B - getD()) % _A) == 0);

		return  (nooverflow && noremainder);
	};

	void encode(value_t value, uint8_t timestamp=0)
	{
		setD(timestamp);
		vc = static_cast<value_coded_t>(value * _A) + _B + timestamp;
	}

	value_t decode() const
	{
		assert(check());
		return (vc - _B - getD()) / _A;
	};

	value_coded_t getCodedValue() const
	{
		return vc;
	};

	void setCodedValue(value_coded_t v)
	{
		vc = v;
	};

	constexpr A_t getA() const
	{
		return _A;
	};

	constexpr B_t getB() const
	{
		return _B;
	};

	constexpr B_t getB() const volatile
	{
		return _B;
	};

	D_t getD() const
	{
		return 0;
	};

	D_t getD() const volatile
	{
		return 0;
	};

	void setD(__attribute__((unused)) D_t val) const volatile {
		// nop
	};


	// Equality operators

	template<class T, B_t Bx = T::B>
	bool operator==(const T& rhs) const
	{
														   /* \/ Compile Time constant!\/ */
		return (static_cast<int16_t>(vc - rhs.getCodedValue()) ==  _B - rhs.getB());
	};

	template<class T, B_t Bx = T::B>
	bool operator==(const volatile T& rhs) const
	{
											   /* \/ Compile Time constant!\/ */
		return (static_cast<int16_t>(vc - rhs.vc) ==  _B - rhs.getB());
	};

	template<typename T, class RET = Encoded_Static<_A, B - T::B> >
	RET eq(const T& t) const
	{
		RET r;
		//r.vc = vc - t.vc;
		r.vc = (this == t); // unencoded comparison
		if(r.vc) {
			//r.vc -= (vc - t.vc) - (Beq - eq);
			r.vc += (vc - t.vc) + (B - T::B - 1);
		} else {
			//r.vc -= (Beq - eq);
			r.vc += (B - T::B);
		}
		//r.D = D - t.D; // TODO
		return r;
	};

	template<class T>
	bool operator!=(const T& rhs) const
	{
		return !(*this == rhs);
	};

	bool operator==(const value_coded_t rhs) const
	{
		return vc - _B - getD() == _A * rhs;
	};

	// Assignment operator
	template<typename T>
	void operator=(const T &rhs) {
		vc = rhs.vc + (B - T::B);
		setD(rhs.getD());
	};

	// Assignment operator
	template<typename T>
	void operator=(const T &rhs) volatile {
		vc = rhs.vc + (B - T::B);
		setD(rhs.getD());
	};

	// Arithmetic operator
	template<typename T, class RET = Encoded_Static<_A, B + T::B> >
	RET operator+(const T& t) const
	{
		RET r;
		r.vc = vc + t.vc;
		//r.D = D + t.D; // TODO
		return r;
	};

	template<typename T>
	Encoded_Static<_A, B> operator+=(const T& t)
	{
		vc += t.vc - T::B;
		return *this;
	};

	template<typename T>
	volatile Encoded_Static<_A, B>& operator+=(const T& t) volatile
	{
		vc += t.vc - T::B;
		return *this;
	};

	template<typename T, class RET = Encoded_Static<_A, B - T::B>>
	RET operator-(const T& t) const
	{
		RET r;
		r.vc = vc - t.vc;
		//r.D = D - t.D; // TODO
		return r;
	};

	template<typename T, class RET = Encoded_Static<_A,  B * T::B>>
	inline RET operator*(const T& t) const
	{
		static_assert(_B * T::B < _A, "product of static signatures (Bs) must be smaller than A");

		RET r;
		value_t x = decode();
		value_t y = t.decode();

		assert((x*T::B + y*_B) < _A) ; // DEBUG

		uint64_t result = (uint64_t) vc * (uint64_t) t.vc;

		/*
		   uint64_t tmp1 = (result / _A % _A) * _A;
		   uint32_t tmp2 = result % _A;
		   result = (result - tmp1) % _A;
		   result += tmp2;
		 */

		result -= (uint64_t) _A * ((uint64_t) x * (uint64_t) T::B + (uint64_t) y * (uint64_t) _B);
		result += ((uint64_t) _A - 1) * (uint64_t) _B * (uint64_t) T::B;
		result /= _A;

		r.vc = result;
		//r.D = 0; // TODO
		return r;
	};

	// Comparison operators

	/*
	// >=0 operator, works but result is not encoded...
	bool geqz() const
	{
		if(vc % _A == B + D) {
			return true;
		} else if(vc % _A == B + D + (__VC_MAX % _A) + 1) {
			return false;
		} else {
			if(DEBUG) kout << (vc % _A) << " != " << B << " + " << D << " + " << (__VC_MAX % _A)+1;
			assert(false);
			return false;
		}
	};

	template<typename T>
	bool operator>=(const T &rhs) const
	{
		return (*this - rhs).geqz();
	};
	*/

	template<typename T, class RET = Encoded_Static<_A, T::B - B> >
	RET operator<=(const T& t) const
	{
		static_assert(T::B > B, "static signature (B) of right operand must be bigger than left");
		RET r;

		// unencoded comparison
		//r.vc = (vc - B - D) <= (t.vc - T::B - t.D);
		r.vc = (vc - B) <= (t.vc - T::B);

		// encoded check of comparison
		value_coded_t diff = t.vc - vc; // this>t  => diff = 2^m - (vc - t.vc)
		// this<=t => diff = t.vc - vc
		value_coded_t sigCond = diff % _A;
		value_coded_t sigPos = T::B - _B;
		value_coded_t sigNeg = (MAXMODA + sigPos) % _A;

		if(r.vc) {
			// expected: sigCond == sigPos
			r.vc += (_A - 1);
		} else {
			// expected: sigCond == sigNeg
			r.vc += (sigPos - sigNeg);
		}
		r.vc += sigCond;
		//r.D = 0; // TODO

		return r;
	};

	template<B_t BIF, typename T, class RET = Encoded_Static<_A, T::B - B + BIF> >
	RET leq(const T& t) const
	{
		static_assert(T::B > B, "static signature (B) of argument must be bigger than own");
		RET r;

		// unencoded comparison
		//r.vc = (vc - B - D) <= (t.vc - T::B - t.D);
		r.vc = (vc - B) <= (t.vc - T::B);

		// encoded check of comparison
		value_coded_t diff = t.vc - vc; // this>t  => diff = 2^m - (vc - t.vc)
		// this<=t => diff = t.vc - vc
		value_coded_t sigCond = diff % _A;
		value_coded_t sigPos = T::B - _B;
		value_coded_t sigNeg = (MAXMODA + sigPos) % _A;

		if(r.vc) {
			// expected: sigCond == sigPos
			r.vc += (_A - 1) + BIF;
		} else {
			// expected: sigCond == sigNeg
			r.vc += (sigPos - sigNeg) + BIF;
		}
		r.vc += sigCond;
		//r.D = 0; // TODO

		return r;
	};
};

template<A_t _A, B_t _B>
class Encoded_Dynamic : Encoded_Static<_A, _B> {
	D_t D;

public:
	Encoded_Dynamic() : Encoded_Static<_A, _B>(), D(0) {};

	constexpr Encoded_Dynamic(value_t value, uint8_t ts) : Encoded_Static<_A, _B>(value), D(ts) {};

	D_t getD() const
	{
		return D;
	};

	void setD(D_t val)
	{
		D = val;
	}
};

// encoded constant
#define EC(b, v) Encoded_Static<A0, b>(v)

#endif /* ENCODED_H_ */
