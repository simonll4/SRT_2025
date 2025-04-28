package ar.edu.srt.model.persistence;

import ar.edu.srt.model.PurchaseOrder;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface PurchaseOrderRepository extends JpaRepository<ar.edu.srt.model.PurchaseOrder, Long> {

    List<PurchaseOrder> findByUserId(Long userId);
}
