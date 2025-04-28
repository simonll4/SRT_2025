package ar.edu.srt.model.serializers;

import ar.edu.srt.model.PurchaseOrder;
import ar.edu.srt.model.OrderItem;
import com.fasterxml.jackson.core.JsonGenerator;
import com.fasterxml.jackson.databind.SerializerProvider;
import com.fasterxml.jackson.databind.ser.std.StdSerializer;

import java.io.IOException;
import java.math.BigDecimal;
import java.time.format.DateTimeFormatter;

public class PurchaseOrderSlimV1JsonSerializer extends StdSerializer<PurchaseOrder> {

    public PurchaseOrderSlimV1JsonSerializer(Class<?> t, boolean dummy) {
        super(t, dummy);
    }


    @Override
    public void serialize(PurchaseOrder order, JsonGenerator jsonGenerator, SerializerProvider serializerProvider)
            throws IOException {

        jsonGenerator.writeStartObject();

        // Campos básicos
        jsonGenerator.writeNumberField("id", order.getId());
        jsonGenerator.writeStringField("status", order.getStatus().name());
        jsonGenerator.writeNumberField("total", order.getTotal().doubleValue());

        if (order.getDescription() != null) {
            jsonGenerator.writeStringField("description", order.getDescription());
        }

        // Formatear fecha
        if (order.getCreatedAt() != null) {
            jsonGenerator.writeStringField(
                    "createdAt",
                    order.getCreatedAt().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME)
            );
        }

        // Información resumida del usuario
        if (order.getUser() != null) {
            jsonGenerator.writeObjectFieldStart("user");
            jsonGenerator.writeNumberField("id", order.getUser().getId());
            jsonGenerator.writeStringField("externalId", order.getUser().getExternalId());
            jsonGenerator.writeStringField("username", order.getUser().getUsername());
            jsonGenerator.writeEndObject();
        }

        // Lista de items con productos y cantidades
        if (order.getItems() != null && !order.getItems().isEmpty()) {
            jsonGenerator.writeArrayFieldStart("items");
            for (OrderItem item : order.getItems()) {
                if (item.getProduct() != null) {
                    jsonGenerator.writeStartObject();
                    jsonGenerator.writeNumberField("productId", item.getProduct().getId());
                    jsonGenerator.writeStringField("productName", item.getProduct().getProduct());
                    jsonGenerator.writeNumberField("quantity", item.getQuantity());
                    jsonGenerator.writeNumberField("unitPrice", item.getUnitPrice().doubleValue());
                    jsonGenerator.writeNumberField("subtotal",
                            item.getUnitPrice().multiply(BigDecimal.valueOf(item.getQuantity())).doubleValue());
                    jsonGenerator.writeEndObject();
                }
            }
            jsonGenerator.writeEndArray();
        }

        jsonGenerator.writeEndObject();
    }
}
