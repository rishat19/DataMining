import java.util.Random;

public class HashFunction<T> {

    private final int mask;

    public HashFunction() {
        this(new Random().nextInt());
    }

    public HashFunction(int mask) {
        this.mask = mask;
    }

    public int hash(T element) {
        return element.hashCode() ^ mask;
    }

    public int getMask() {
        return mask;
    }

}
