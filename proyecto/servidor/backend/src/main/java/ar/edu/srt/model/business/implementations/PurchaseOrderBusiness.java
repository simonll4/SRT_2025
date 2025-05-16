package ar.edu.srt.model.business.implementations;

import ar.edu.srt.model.PurchaseOrder;
import ar.edu.srt.model.Product;
import ar.edu.srt.model.User;
import ar.edu.srt.model.OrderItem;
import ar.edu.srt.model.business.exceptions.BusinessException;
import ar.edu.srt.model.business.exceptions.FoundException;
import ar.edu.srt.model.business.exceptions.NotFoundException;
import ar.edu.srt.model.business.interfaces.IPurchaseOrderBusiness;
import ar.edu.srt.model.persistence.PurchaseOrderRepository;
import ar.edu.srt.model.persistence.ProductRepository;
import ar.edu.srt.model.persistence.UserRepository;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

import static java.sql.DriverManager.println;


@Service
@Slf4j
public class PurchaseOrderBusiness implements IPurchaseOrderBusiness {

    @Autowired
    private PurchaseOrderRepository purchaseOrderDAO;

    @Autowired
    private ProductRepository productDAO;

    @Autowired
    private UserRepository userDAO;

    @Autowired
    private UserBusiness userBusiness;

    @Override
    public PurchaseOrder load(Long id) throws NotFoundException, BusinessException {
        Optional<PurchaseOrder> orderFound;
        try {
            orderFound = purchaseOrderDAO.findById(id);
        } catch (Exception e) {
            log.error(e.getMessage(), e);
            throw BusinessException.builder().ex(e).build();
        }
        if (orderFound.isEmpty()) {
            throw NotFoundException.builder().message("No se encuentra la Orden id= " + id).build();
        }
        return orderFound.get();
    }

    @Override
    public List<PurchaseOrder> list() throws BusinessException {
        try {
            return purchaseOrderDAO.findAll();
        } catch (Exception e) {
            log.error(e.getMessage(), e);
            throw BusinessException.builder().ex(e).build();
        }
    }


    @Override
    @Transactional
    public PurchaseOrder add(PurchaseOrder purchaseOrder) throws BusinessException, NotFoundException {
        // 1. Validar usuario
        User user = purchaseOrder.getUser();
        if (user == null || user.getExternalId() == null) {
            throw BusinessException.builder()
                    .message("La orden debe tener un usuario con externalId asociado")
                    .build();
        }

        // 2. Buscar usuario en BD
        User managedUser = userDAO.findByExternalId(user.getExternalId())
                .orElseThrow(() -> NotFoundException.builder()
                        .message("No se encuentra el Usuario externalId= " + user.getExternalId())
                        .build());

        // 3. Validar items
        if (purchaseOrder.getItems() == null || purchaseOrder.getItems().isEmpty()) {
            throw BusinessException.builder()
                    .message("La orden debe contener al menos un producto")
                    .build();
        }

        // 4. Procesar items y calcular total
        BigDecimal total = BigDecimal.ZERO;
        List<OrderItem> managedItems = new ArrayList<>();

        for (OrderItem item : purchaseOrder.getItems()) {
            // Validar cantidad
            if (item.getQuantity() <= 0) {
                throw BusinessException.builder()
                        .message("La cantidad debe ser mayor a cero para el producto id= " +
                                (item.getProduct() != null ? item.getProduct().getId() : "null"))
                        .build();
            }

            // Buscar producto en BD
            // Product managedProduct = productDAO.findById(item.getProduct().getId())
            //         .orElseThrow(() -> NotFoundException.builder()
            //                 .message("No se encuentra el Producto id= " + item.getProduct().getId())
            //                 .build());
            
            Product managedProduct = productDAO.findByProduct(item.getProduct().getProduct())
                .orElseThrow(() -> NotFoundException.builder()
                        .message("No se encuentra el Producto= " + item.getProduct().getId())
                        .build());

            // Configurar el item con los objetos gestionados
            item.setProduct(managedProduct);
            item.setUnitPrice(managedProduct.getPrice()); // Guardar precio actual
            item.setOrder(purchaseOrder); // Establecer relación bidireccional
            managedItems.add(item);

            // Calcular subtotal
            BigDecimal itemTotal = managedProduct.getPrice().multiply(BigDecimal.valueOf(item.getQuantity()));
            total = total.add(itemTotal);
        }

        // 5. Configurar la orden
        purchaseOrder.setUser(managedUser);
        purchaseOrder.setStatus(PurchaseOrder.OrderStatus.PENDING);
        purchaseOrder.setTotal(total);
        purchaseOrder.setItems(managedItems);
        purchaseOrder.setCreatedAt(LocalDateTime.now());

        // 6. Validar saldo
        if (total.compareTo(managedUser.getBalance()) > 0) {
            purchaseOrder.setStatus(PurchaseOrder.OrderStatus.FAILED);
            purchaseOrder.setDescription("Saldo insuficiente para completar la orden");
        }

        // 7. Guardar la orden
        try {
            return purchaseOrderDAO.save(purchaseOrder);
        } catch (Exception e) {
            log.error("Error al crear la orden", e);
            throw BusinessException.builder()
                    .message("Error al crear la Orden: " + e.getMessage())
                    .build();
        }
    }

    @Override
    public PurchaseOrder completeOrder(PurchaseOrder order) throws NotFoundException, BusinessException, FoundException {
        PurchaseOrder orderFound = load(order.getId());

        // Validar que la orden esté pendiente
        if (orderFound.getStatus() != PurchaseOrder.OrderStatus.PENDING) {
            throw BusinessException.builder()
                    .message("Solo se pueden completar órdenes en estado PENDING")
                    .build();
        }

        User user = orderFound.getUser();
        BigDecimal total = orderFound.getTotal();
        if (total.compareTo(user.getBalance()) > 0) {
            orderFound.setStatus(PurchaseOrder.OrderStatus.FAILED);
            orderFound.setDescription("Saldo insuficiente para completar la orden");
        } else {
            user.setBalance(user.getBalance().subtract(total));
            userBusiness.update(user);
            orderFound.setDescription("Orden completada con éxito");
        }


        // Actualizar estado
        orderFound.setStatus(PurchaseOrder.OrderStatus.COMPLETED);

        try {
            return purchaseOrderDAO.save(orderFound);
        } catch (Exception e) {
            log.error(e.getMessage(), e);
            throw BusinessException.builder().message("Error al completar la orden").build();
        }
    }

    @Override
    public PurchaseOrder cancelOrder(PurchaseOrder order) throws NotFoundException, BusinessException {
        PurchaseOrder orderFound = load(order.getId());

        // Validar que la orden esté pendiente
        if (orderFound.getStatus() != PurchaseOrder.OrderStatus.PENDING) {
            throw BusinessException.builder()
                    .message("Solo se pueden cancelar órdenes en estado PENDING")
                    .build();
        }

        // Actualizar estado
        orderFound.setStatus(PurchaseOrder.OrderStatus.FAILED);

        // Actualizar descripción
        if (order.getDescription() != null) {
            orderFound.setDescription(order.getDescription());
        }

        try {
            return purchaseOrderDAO.save(orderFound);
        } catch (Exception e) {
            log.error(e.getMessage(), e);
            throw BusinessException.builder().message("Error al cancelar la orden").build();
        }
    }

    @Override
    public PurchaseOrder updateOrderItems(List<OrderItem> itemsToUpdate)
            throws NotFoundException, BusinessException {

        // 1. Cargar la orden completa
        Long orderId = itemsToUpdate.get(0).getOrder().getId();

        println("ID de la orden a actualizar: " + orderId);

        PurchaseOrder order = load(orderId);

        // 2. Validar que esté en estado PENDING
        if (order.getStatus() != PurchaseOrder.OrderStatus.PENDING) {
            throw BusinessException.builder()
                    .message("Solo se pueden modificar órdenes en estado PENDING")
                    .build();
        }

        // 3. Procesar cada item a actualizar
        for (OrderItem updateItem : itemsToUpdate) {
            // Validar que el item pertenezca a esta orden
            if (!orderId.equals(updateItem.getOrder().getId())) {
                throw BusinessException.builder()
                        .message("El item no pertenece a esta orden")
                        .build();
            }

            // Buscar el item existente
            OrderItem existingItem = order.getItems().stream()
                    .filter(item -> item.getId().equals(updateItem.getId()))
                    .findFirst()
                    .orElseThrow(() -> NotFoundException.builder()
                            .message("No se encuentra el item con id " + updateItem.getId())
                            .build());

            // Validar que el producto no haya cambiado
            if (!existingItem.getProduct().getId().equals(updateItem.getProduct().getId())) {
                throw BusinessException.builder()
                        .message("No se puede cambiar el producto de un item existente")
                        .build();
            }

            // Validar cantidad
            if (updateItem.getQuantity() <= 0) {
                // Eliminar el item si la cantidad es cero o negativa
                order.getItems().remove(existingItem);
            } else {
                // Actualizar cantidad
                existingItem.setQuantity(updateItem.getQuantity());
            }
        }

        // 4. Recalcular el total
        BigDecimal newTotal = calculateOrderTotal(order);
        order.setTotal(newTotal);

        // 5. Si no quedan items, marcar como FAILED
        if (order.getItems().isEmpty()) {
            order.setStatus(PurchaseOrder.OrderStatus.FAILED);
            order.setDescription("Orden vaciada - Sin productos");
        }

        // 6. Guardar cambios
        try {
            return purchaseOrderDAO.save(order);
        } catch (Exception e) {
            log.error("Error al actualizar items de la orden", e);
            throw BusinessException.builder()
                    .message("Error al actualizar items de la orden")
                    .build();
        }
    }

    private BigDecimal calculateOrderTotal(PurchaseOrder order) {
        return order.getItems().stream()
                .map(item -> item.getUnitPrice().multiply(BigDecimal.valueOf(item.getQuantity())))
                .reduce(BigDecimal.ZERO, BigDecimal::add);
    }

}