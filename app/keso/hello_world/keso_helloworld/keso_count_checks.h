#ifndef __keso_count_checks_h__
#define __keso_count_checks_h__ 1

/*
 * NOTE: This file is generated. Any edits will be overwritten.
 * Instead of editing this file, edit the template files mentioned below.
 */

/*********************************************************
 * Generated from c-templates/CodeTemplate/countChecks.c *
 *********************************************************/
#ifdef KESO_COUNT_CHECKS
extern unsigned int keso_checkcounts[];
#define KESO_COUNT_CHECK(CHK_ID) keso_checkcounts[CHK_ID]++
#else  /* defined(KESO_COUNT_CHECKS) */
#define KESO_COUNT_CHECK(CHK_ID)
#endif /* defined(KESO_COUNT_CHECKS) */
#endif
