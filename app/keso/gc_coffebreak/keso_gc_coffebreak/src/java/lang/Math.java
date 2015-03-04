// @formatter:off
/**(c)

  Copyright (C) 2006-2013 Christian Wawersich, Michael Stilkerich,
                          Christoph Erhardt

  This file is part of the KESO Java Runtime Environment.

  KESO is free software: you can redistribute it and/or modify it under the
  terms of the Lesser GNU General Public License as published by the Free
  Software Foundation, either version 3 of the License, or (at your option)
  any later version.

  KESO is distributed in the hope that it will be useful, but WITHOUT ANY
  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
  FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for
  more details. You should have received a copy of the GNU Lesser General
  Public License along with KESO. If not, see <http://www.gnu.org/licenses/>.

  Please contact keso@cs.fau.de for more info.

  (c)**/
// @formatter:on

package java.lang;

public final class Math {
	public static final double E  = 2.7182818284590452354;
	public static final double PI = 3.14159265358979323846;

	public static int abs(int x) {
		return (x < 0 ? -x : x);
	}

	public static long abs(long x) {
		return (x < 0 ? -x : x);
	}

	public static float abs(float x) {
		return (x < 0 ? -x : x);
	}

	public static double abs(double x) {
		return (x < 0.0 ? -x : x);
	}

	public static double ceil(double x) {
		return -floor(-x);
	}

	public static double cos(double x) {
		x = (x + PI) % (2 * PI) - PI;
		double x2 = x * x;
		return 1.0 - x2 * (1.0/2 + x2 * (1.0/24 - x2 * (1.0/720)));
	}

	public static double floor(double x) {
		return x - (x % 1.0d);
	}

	public static int max(int a, int b) {
		return (a < b ? b : a);
	}

	public static long max(long a, long b) {
		return (a < b ? b : a);
	}

	public static float max(float a, float b) {
		return (a < b ? b : a);
	}

	public static double max(double a, double b) {
		return (a < b ? b : a);
	}

	public static int min(int a, int b) {
		return (a < b ? a : b);
	}

	public static long min(long a, long b) {
		return (a < b ? a : b);
	}

	public static float min(float a, float b) {
		return (a < b ? a : b);
	}

	public static double min(double a, double b) {
		return (a < b ? a : b);
	}

	public static double sin(double x) {
		x = (x + PI) % (2 * PI) - PI;
		double x2 = x * x;
		return x * (1.0 - x2 * (1.0/6 + x2 * (1.0/120 - x2 * (1.0/5040))));
	}

	public static double sqrt(double x) {
		return pow(x, 0.5d);
	}

	public static double tan(double x) {
		return sin(x) / cos(x);
	}

	public static float toDegrees(float angrad) {
		return angrad * 180.0f / (float) PI;
	}

	public static float toRadians(float angdeg) {
		return angdeg * (float) PI / 180.0f;
	}

	public static double toDegrees(double angrad) {
		return angrad * 180.0 / PI;
	}

	public static double toRadians(double angdeg) {
		return angdeg * PI / 180.0;
	}

	// not CLDC
	public static double rint(double x) {
		double f = x % 1.0d;
		double i = x - f;

		if (f == 0.5)
			return (i % 2.0d == 0.0) ? i : i + 1.0d;
		if (f < 0.5)
			return i;
		if (f > 0.5)
			return i + 1.0d;

		return Double.NaN;
	}

	public static int round(float x) {
		if (Float.isNaN(x))
			return 0;
		if (x <= Integer.MIN_VALUE)
			return Integer.MIN_VALUE;
		if (x >= Integer.MAX_VALUE)
			return Integer.MAX_VALUE;
		return (int) floor(x + 0.5f);
	}

	public static long round(double x) {
		if (Double.isNaN(x))
			return 0;
		if (x <= Long.MIN_VALUE)
			return Long.MIN_VALUE;
		if (x >= Long.MAX_VALUE)
			return Long.MAX_VALUE;
		return (long) floor(x + 0.5d);
	}

	public static double IEEEremainder(double x, double y) {
		if (Double.isNaN(x) || Double.isNaN(y))
			return Double.NaN;
		if (Double.isInfinite(x))
			return Double.NaN;
		if (y == 0.0)
			return Double.NaN;
		if (Double.isInfinite(y))
			return x;
		double n = rint(x / y);
		return x - y * n;
	}

	public static double exp(double x) {
		return 1.0 + x *
			(1.0 + x *
			 (1.0/2 + x *
				(1.0/6 + x *
				 (1.0/24 + x *
					(1.0/120 + x *
					 (1.0/720))))));
	}

	public static double pow(double x, double y) {
		return exp(log(x) * y);
	}

	public static double log(double x) {
		if (x < 0.0d)
			return Double.NaN;
		if (x == 0.0d)
			return Double.NEGATIVE_INFINITY;
		if (x < 1.0d)
			return -log(1.0d / x);
		if (x == 1.0d)
			return 0.0d;

		double v0 = 0.0d;
		double v1 = 750.0d;
		double v = Double.NaN;
		for (int i = 0; i < 64; i++)
		{
			v = (v0 + v1) / 2;
			double xm = exp(v);
			if (x == xm)
				break;
			else if (x > xm)
				v0 = v;
			else if (x < xm)
				v1 = v;
		}

		return v;
	}

	public static double asin(double x) {
		if (x > 1.0d)
			return Double.NaN;
		if (x == 1.0d)
			return PI/2;
		if (x < -1.0d)
			return Double.NaN;
		if (x == -1.0d)
			return -PI/2;

		double v0 = -PI/2;
		double v1 = PI/2;
		double v = Double.NaN;
		for (int i = 0; i < 64; i++)
		{
			v = (v0 + v1) / 2;
			double xm = sin(v);
			if (x == xm)
				break;
			else if (x > xm)
				v0 = v;
			else if (x < xm)
				v1 = v;
		}

		return v;
	}

	public static double acos(double x) {
		if (x > 1.0d)
			return Double.NaN;
		if (x == 1.0d)
			return 0.0d;
		if (x < -1.0d)
			return Double.NaN;
		if (x == -1.0d)
			return PI;

		double v0 = 0;
		double v1 = PI;
		double v = Double.NaN;
		for (int i = 0; i < 64; i++)
		{
			v = (v0 + v1) / 2;
			double xm = cos(v);
			if (x == xm)
				break;
			else if (x > xm)
				v1 = v;
			else if (x < xm)
				v0 = v;
		}

		return v;
	}

	public static double atan(double x) {
		if (x == Double.POSITIVE_INFINITY)
			return PI/2;
		if (x == Double.NEGATIVE_INFINITY)
			return -PI/2;

		double v0 = -PI/2;
		double v1 = PI/2;
		double v = Double.NaN;
		for (int i = 0; i < 64; i++)
		{
			v = (v0 + v1) / 2;
			double xm = tan(v);
			if (x == xm)
				break;
			else if (x > xm)
				v0 = v;
			else if (x < xm)
				v1 = v;
		}

		return v;
	}

	public static double atan2(double y, double x) {
		double a = atan(y / x);
		return	(y > 0)
			? a
			: (x > 0)
			? a + PI
			: a - PI;
	}
}
