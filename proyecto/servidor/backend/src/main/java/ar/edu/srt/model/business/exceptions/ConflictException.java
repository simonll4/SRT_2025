package ar.edu.srt.model.business.exceptions;

import lombok.Builder;

import java.io.Serial;

public class ConflictException extends Exception {

    @Serial
    private static final long serialVersionUID = 1L;

    @Builder
    public ConflictException(String message, Throwable ex) {
        super(message, ex);
    }

    @Builder
    public ConflictException(String message) {
        super(message);
    }

    @Builder
    public ConflictException(Throwable ex) {
        super(ex.getMessage(), ex);
    }
}



