package ar.edu.srt.model.business.exceptions;

import lombok.Builder;
import lombok.NoArgsConstructor;

import java.io.Serial;

@NoArgsConstructor
public class BadRequestException extends Exception {
    @Serial
    private static final long serialVersionUID = 1L;

    @Builder
    public BadRequestException(String message, Throwable ex) {
        super(message, ex);
    }
    @Builder
    public BadRequestException(String message) {
        super(message);
    }
    @Builder
    public BadRequestException(Throwable ex) {
        super(ex.getMessage(), ex);
    }

}
