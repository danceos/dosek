#ifndef ASSERT_H_
#define ASSERT_H_

// runtime assert, print assertion if debugging, cause trap
#if DEBUG
#define assert(x) { if((x)==0) { \
    kout << "ASSERT " << __FILE__ << ":" << __LINE__ << " " << __func__ << endl; \
    __asm__("hlt");}}
#else
#define assert(x) { if((x)==0) __asm__("ud2"); }
#endif

// template assert for compile-time checks
template <bool B>
struct tAssert
{
};

template<> struct tAssert<true>
{
    static void Assert() {};
};

#define TAssert(a) {const bool b = (const bool) (a); tAssert<b>::Assert();}

#endif /* ASSERT_H_ */
