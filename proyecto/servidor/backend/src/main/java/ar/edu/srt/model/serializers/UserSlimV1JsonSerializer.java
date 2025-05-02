package ar.edu.srt.model.serializers;


import ar.edu.srt.model.User;
import com.fasterxml.jackson.core.JsonGenerator;
import com.fasterxml.jackson.databind.SerializerProvider;
import com.fasterxml.jackson.databind.ser.std.StdSerializer;

import java.io.IOException;

public class UserSlimV1JsonSerializer extends StdSerializer<User> {

    public UserSlimV1JsonSerializer(Class<?> t, boolean dummy) {
        super(t, dummy);
    }

    @Override
    public void serialize(User user, JsonGenerator jsonGenerator, SerializerProvider serializerProvider) throws IOException {
        jsonGenerator.writeStartObject(); // Inicia el objeto JSON
        jsonGenerator.writeNumberField("id", user.getId()); // Serializa el campo id
        jsonGenerator.writeStringField("externalId", user.getExternalId());
        jsonGenerator.writeStringField("username", user.getUsername()); // Serializa el campo username
        jsonGenerator.writeStringField("surname", user.getSurname());
        jsonGenerator.writeNumberField("balance", user.getBalance().doubleValue());
        jsonGenerator.writeBooleanField("enabled", user.isEnabled()); // Serializa el campo enabled
        jsonGenerator.writeEndArray();
        jsonGenerator.writeEndObject(); // Finaliza el objeto JSON
    }



}
