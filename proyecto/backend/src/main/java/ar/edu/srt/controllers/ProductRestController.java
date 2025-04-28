package ar.edu.srt.controllers;

import ar.edu.srt.Constants;
import ar.edu.srt.model.Product;
import ar.edu.srt.model.business.interfaces.IProductBusiness;
import ar.edu.srt.model.serializers.ProductSlimV1JsonSerializer;
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
@RequestMapping(Constants.URL_PRODUCTS)
public class ProductRestController {

    @Autowired
    private IProductBusiness productBusiness;


    @SneakyThrows
    @GetMapping(value = "", produces = MediaType.APPLICATION_JSON_VALUE)
    public ResponseEntity<?> list() {

        List<Product> products = productBusiness.list();

        StdSerializer<Product> productSerializer = new ProductSlimV1JsonSerializer(Product.class, false);
        ObjectMapper mapper = JsonUtils.getObjectMapper(Product.class, productSerializer, null);

        List<Object> serializedProducts = products.stream()
                .map(product -> {
                    try {
                        return mapper.valueToTree(product);
                    } catch (Exception e) {
                        throw new RuntimeException("Error al serializar el objeto Product", e);
                    }
                }).toList();

        return new ResponseEntity<>(serializedProducts, HttpStatus.OK);
    }

    @SneakyThrows
    @GetMapping(value = "/{id}")
    public ResponseEntity<?> loadProduct(@PathVariable long id) {
        return new ResponseEntity<>(productBusiness.load(id), HttpStatus.OK);
    }

    @SneakyThrows
    @GetMapping(value = "/by_name/{product}", produces = MediaType.APPLICATION_JSON_VALUE)
    public ResponseEntity<?> loadProduct(@PathVariable String product) {
        return new ResponseEntity<>(productBusiness.load(product), HttpStatus.OK);
    }

    @SneakyThrows
    @PostMapping(value = "")
    public ResponseEntity<?> addProduct(@Valid @RequestBody Product product) {
        Product response = productBusiness.add(product);
        HttpHeaders responseHeaders = new HttpHeaders();
        responseHeaders.set("location", Constants.URL_PRODUCTS + "/" + response.getId());
        return new ResponseEntity<>(responseHeaders, HttpStatus.CREATED);
    }

    @SneakyThrows
    @PutMapping(value = "")
    public ResponseEntity<?> updateProduct(@RequestBody Product product) {
        productBusiness.update(product);
        return new ResponseEntity<>(HttpStatus.OK);
    }

    @SneakyThrows
    @DeleteMapping(value = "/{id}")
    public ResponseEntity<?> deleteProduct(@PathVariable long id) {
        productBusiness.delete(id);
        return new ResponseEntity<String>(HttpStatus.OK);
    }

}
