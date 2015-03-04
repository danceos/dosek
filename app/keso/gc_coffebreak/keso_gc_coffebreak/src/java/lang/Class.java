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

public final class Class<T> {
    public String getName() { return null; }

    public boolean isInterface() { return false; }

    public static Class<?> getPrimitiveClass(String cname) { return null ; }

    public String toString() {
			return (isInterface() ? "interface " : "class ") + getName();
    }

    //public static Class forName(String className) throws ClassNotFoundException { }

    public Class getComponentType() {
			throw new Error("not implemented");
		}

    //public boolean isInstance(Object o) { throw new Error("NOT IMPLEMENTED"); }

    //public Method[] getDeclaredMethods()  { throw new Error("NOT IMPLEMENTED"); }

    //public Class getSuperclass() { return null; }

    //public Class[] getInterfaces() { return null; }

    //public ClassLoader getClassLoader() { throw new Error("NOT IMPLEMENTED"); }

    public Object newInstance() throws InstantiationException, IllegalAccessException {
			throw new Error("not implemented");
		}

    // public boolean isAssignableFrom(Class c) { throw new Error("NOT IMPLEMENTED"); }

}
