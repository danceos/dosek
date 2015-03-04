package keso.core;

import java.lang.annotation.NoHeapAllocation;

public final class IntPtr implements Comparable<IntPtr> {
    private int address;

    public IntPtr() {
        this(0);
    }

    public IntPtr(int value)
    {
        this.address = value;
    }

    @NoHeapAllocation
    public int getInt()
    {
        return this.address;
    }

    @NoHeapAllocation
    public void add(int offset)
    {
        this.address += offset;
    }

    @NoHeapAllocation
    public void setAddress(int value) {
        this.address = value;
    }

    @NoHeapAllocation
    private void subtract(int value)
    {
        this.address -= value;
    }

    @NoHeapAllocation
    public void subtract(IntPtr other)
    {
        this.subtract(other.getInt());
    }

    @NoHeapAllocation
    @Override
    public int compareTo(IntPtr other) {
        return this.address - other.getInt();
    }
}
