package ar.edu.srt.controllers;

import ar.edu.srt.Constants;
import ar.edu.srt.model.PurchaseOrder;
import ar.edu.srt.model.business.interfaces.IPurchaseOrderBusiness;
import ar.edu.srt.model.serializers.PurchaseOrderSlimV1JsonSerializer;
import ar.edu.srt.util.JsonUtils;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.ser.std.StdSerializer;
import jakarta.validation.Valid;
import lombok.SneakyThrows;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping(Constants.URL_PURCHASE_ORDERS)
public class PurchaseOrderRestController {

    @Autowired
    private IPurchaseOrderBusiness purchaseOrderBusiness;

    @SneakyThrows
    @GetMapping(value = "", produces = MediaType.APPLICATION_JSON_VALUE)
    public ResponseEntity<?> list() {
        List<PurchaseOrder> orders = purchaseOrderBusiness.list();
        StdSerializer<PurchaseOrder> serializer = new PurchaseOrderSlimV1JsonSerializer(PurchaseOrder.class, false);
        ObjectMapper mapper = JsonUtils.getObjectMapper(PurchaseOrder.class, serializer, null);
        List<Object> serializedOrders = orders.stream().map(order -> {
            try {
                return mapper.valueToTree(order);
            } catch (Exception e) {
                throw new RuntimeException("Error al serializar PurchaseOrder", e);
            }
        }).toList();
        return new ResponseEntity<>(serializedOrders, HttpStatus.OK);
    }

    @SneakyThrows
    @GetMapping(value = "/{id}")
    public ResponseEntity<?> loadOrder(@PathVariable Long id) {
        PurchaseOrder order = purchaseOrderBusiness.load(id);
        StdSerializer<PurchaseOrder> serializer = new PurchaseOrderSlimV1JsonSerializer(PurchaseOrder.class, false);
        ObjectMapper mapper = JsonUtils.getObjectMapper(PurchaseOrder.class, serializer, null);
        Object serializedOrder = mapper.valueToTree(order);
        return new ResponseEntity<>(serializedOrder, HttpStatus.OK);
    }

    @SneakyThrows
    @PostMapping(value = "")
    public ResponseEntity<?> addOrder(@Valid @RequestBody PurchaseOrder order) {
        PurchaseOrder response = purchaseOrderBusiness.add(order);
        StdSerializer<PurchaseOrder> serializer = new PurchaseOrderSlimV1JsonSerializer(PurchaseOrder.class, false);
        ObjectMapper mapper = JsonUtils.getObjectMapper(PurchaseOrder.class, serializer, null);
        Object serializedOrder = mapper.valueToTree(response);
        return new ResponseEntity<>(serializedOrder, HttpStatus.OK);
    }


    @SneakyThrows
    @PostMapping(value = "/complete")
    public ResponseEntity<?> completeOrder(@RequestBody PurchaseOrder order) {
        PurchaseOrder response = purchaseOrderBusiness.completeOrder(order);
        HttpHeaders responseHeaders = new HttpHeaders();
        responseHeaders.set("location", Constants.URL_PRODUCTS + "/" + response.getId());
        return new ResponseEntity<>(responseHeaders, HttpStatus.OK);
    }

    @SneakyThrows
    @PostMapping(value = "/cancel")
    public ResponseEntity<?> cancelOrder(@RequestBody PurchaseOrder order) {
        PurchaseOrder response = purchaseOrderBusiness.cancelOrder(order);
        HttpHeaders responseHeaders = new HttpHeaders();
        responseHeaders.set("location", Constants.URL_PRODUCTS + "/" + response.getId());
        return new ResponseEntity<>(responseHeaders, HttpStatus.OK);
    }
}

