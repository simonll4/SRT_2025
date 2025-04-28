package ar.edu.srt.model;


import com.fasterxml.jackson.annotation.JsonIgnore;
import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.persistence.*;
import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.NotNull;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;


import java.math.BigDecimal;
import java.util.HashSet;
import java.util.Set;

@Entity
@Table(name = "users")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class User {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(columnDefinition = "tinyint default 1")
    private boolean enabled = true;

    @Column(unique = true, nullable = false)
    private String externalId;

    @Column(length = 100)
    private String username;

    @Column(length = 100)
    private String surname;

    @NotNull
    @DecimalMin("0.00")
    @Column(precision = 15, scale = 2)
    private BigDecimal balance = BigDecimal.ZERO;

    // Relación UNO-A-MUCHOS con PurchaseOrder
    @OneToMany(mappedBy = "user", cascade = CascadeType.ALL)
    private Set<PurchaseOrder> orders = new HashSet<>();
}