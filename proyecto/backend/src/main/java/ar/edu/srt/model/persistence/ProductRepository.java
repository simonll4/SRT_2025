package ar.edu.srt.model.persistence;

import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import ar.edu.srt.model.Product;

@Repository
public interface ProductRepository extends JpaRepository<Product, Long> {

    Optional<Product> findByProduct(String product);

    Optional<Product> findByProductAndIdNot(String product, Long id);

}
