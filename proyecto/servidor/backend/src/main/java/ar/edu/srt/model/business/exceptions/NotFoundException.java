package ar.edu.srt.model.business.exceptions;

import lombok.Builder;
import lombok.NoArgsConstructor;

import java.io.Serial;

@NoArgsConstructor
public class NotFoundException extends Exception {

	@Serial
	private static final long serialVersionUID = 1L;

	@Builder
	public NotFoundException(String message, Throwable ex) {
		super(message, ex);
	}
	@Builder
	public NotFoundException(String message) {
		super(message);
	}
	@Builder
	public NotFoundException(Throwable ex) {
		super(ex.getMessage(), ex);
	}
}
