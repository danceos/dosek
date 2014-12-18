// @formatter:off
/**(c)
 * 
 *  Copyright (C) 2006-2013 Christian Wawersich, Michael Stilkerich,
 *                          Christoph Erhardt
 * 
 *  This file is part of the KESO Java Runtime Environment.
 * 
 *  KESO is free software: you can redistribute it and/or modify it under the
 *  terms of the Lesser GNU General Public License as published by the Free
 *  Software Foundation, either version 3 of the License, or (at your option)
 *  any later version.
 * 
 *  KESO is distributed in the hope that it will be useful, but WITHOUT ANY
 *  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
 *  FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for
 *  more details. You should have received a copy of the GNU Lesser General
 *  Public License along with KESO. If not, see <http://www.gnu.org/licenses/>.
 * 
 *  Please contact keso@cs.fau.de for more info.
 * 
 *  (c)**/
// @formatter:on
package test_inline;

import keso.core.TaskService;

public class HelloWorld_final implements Runnable {
	
	private A a1;
	private A a2;
	private E e;
	private F f;
	private G g;
		
	public HelloWorld_final() {
		a1 = new A();
		a2 = new A();
		e = new E();
		System.out.println("HelloWorld constructor\n");
	}
	
	public void run() {
		System.out.println(System.getProperty("ddom1.ttask1.HelloString","Hello World!"));
		System.out.println("You successfully compiled and ran KESO. Goodbye...\n");
		a1.info();
		a2.info();
		e.info();
	}
	
}
