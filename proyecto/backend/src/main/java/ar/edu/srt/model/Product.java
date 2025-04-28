package ar.edu.srt.model;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.persistence.*;
import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.NotNull;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.math.BigDecimal;

@Entity
@Table(name = "products")
@Inheritance(strategy = InheritanceType.JOINED)
@AllArgsConstructor
@NoArgsConstructor
@Getter
@Setter
public class Product {

    @Schema(hidden = true)
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @NotEmpty(message = "El atributo 'product' no puede estar vacío")
    @Column(length = 100, unique = true)
    private String product;

    @Column(precision = 10, scale = 2)
    @NotNull(message = "El precio no puede ser nulo")
    private BigDecimal price;

}
