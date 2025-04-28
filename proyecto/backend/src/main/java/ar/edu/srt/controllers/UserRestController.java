package ar.edu.srt.controllers;

import ar.edu.srt.Constants;

import ar.edu.srt.model.User;
import ar.edu.srt.model.business.interfaces.IUserBusiness;
import ar.edu.srt.model.serializers.UserSlimV1JsonSerializer;
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
@RequestMapping(Constants.URL_USERS)
public class UserRestController {

    @Autowired
    private IUserBusiness userBusiness;


    @SneakyThrows
    @GetMapping(value = "/external-id/{id}", produces = MediaType.APPLICATION_JSON_VALUE)
    public ResponseEntity<?> loadUser(@PathVariable String id) {

        User user = userBusiness.load(id);
        StdSerializer<User> userSerializer = new UserSlimV1JsonSerializer(User.class, false);
        ObjectMapper mapper = JsonUtils.getObjectMapper(User.class, userSerializer, null);
        Object serializedUser = mapper.valueToTree(user);
        return new ResponseEntity<>(serializedUser, HttpStatus.OK);
    }

    @SneakyThrows
    @GetMapping(value = "", produces = MediaType.APPLICATION_JSON_VALUE)
    public ResponseEntity<?> list() {

        List<User> users = userBusiness.list();

        StdSerializer<User> userSerializer = new UserSlimV1JsonSerializer(User.class, false);
        ObjectMapper mapper = JsonUtils.getObjectMapper(User.class, userSerializer, null);

        List<Object> serializedUsers = users.stream()
                .map(user -> {
                    try {
                        return mapper.valueToTree(user);
                    } catch (Exception e) {
                        throw new RuntimeException("Error al serializar el objeto User", e);
                    }
                }).toList();

        return new ResponseEntity<>(serializedUsers, HttpStatus.OK);
    }


    @SneakyThrows
    @PostMapping(value = "", produces = MediaType.APPLICATION_JSON_VALUE)
    public ResponseEntity<?> add(@Valid @RequestBody User user) {
        User response = userBusiness.add(user);
        HttpHeaders responseHeaders = new HttpHeaders();
        responseHeaders.set("Location", Constants.URL_USERS + "/" + response.getId());
        return new ResponseEntity<>(responseHeaders, HttpStatus.CREATED);
    }

    @SneakyThrows
    @PutMapping(value = "", produces = MediaType.APPLICATION_JSON_VALUE)
    public ResponseEntity<?> update(@Valid @RequestBody User user) {
        userBusiness.update(user);
        return new ResponseEntity<>(HttpStatus.OK);
    }


    @SneakyThrows
    @DeleteMapping(value = "/{id}", produces = MediaType.APPLICATION_JSON_VALUE)
    public ResponseEntity<?> delete(@PathVariable Long id) {
        userBusiness.delete(id);
        return new ResponseEntity<>(HttpStatus.OK);
    }

}