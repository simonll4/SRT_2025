package ar.edu.srt.model.business.implementations;

import ar.edu.srt.model.PurchaseOrder;
import ar.edu.srt.model.Product;
import ar.edu.srt.model.User;
import ar.edu.srt.model.business.OrderItem;
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
    public PurchaseOrder add(PurchaseOrder purchaseOrder) throws FoundException, BusinessException, NotFoundException {
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
            Product managedProduct = productDAO.findById(item.getProduct().getId())
                    .orElseThrow(() -> NotFoundException.builder()
                            .message("No se encuentra el Producto id= " + item.getProduct().getId())
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
            purchaseOrder.setDescription("Saldo insuficiente. Saldo actual: " +
                    managedUser.getBalance() + ", Total requerido: " + total);
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


//    @Override
//    @Transactional
//    public PurchaseOrder add(PurchaseOrder purchaseOrder) throws FoundException, BusinessException, NotFoundException {
//        // Verificar si la orden ya existe

    /// /        if (purchaseOrder.getId() != null) {
    /// /            Optional<PurchaseOrder> existingOrder = purchaseOrderDAO.findById(purchaseOrder.getId());
    /// /            if (existingOrder.isPresent()) {
    /// /                throw FoundException.builder().message("Ya existe la Orden id= " + purchaseOrder.getId()).build();
    /// /            }
    /// /        }
//
//        // Verificar si existe externalId del user
//        User user = purchaseOrder.getUser();
//        if (user == null || user.getExternalId() == null) {
//            throw BusinessException.builder().message("La orden debe tener un usuario con externalId asociado").build();
//        }
//
//        // verificar si el usuario existe
//        Optional<User> userFound = userDAO.findByExternalId(user.getExternalId());
//        if (userFound.isEmpty()) {
//            throw NotFoundException.builder().message("No se encuentra el Usuario externalId= " + user.getExternalId()).build();
//        }
//
//        // Verificar productos
//        Set<Product> products = purchaseOrder.getProducts();
//        if (products == null || products.isEmpty()) {
//            throw BusinessException.builder().message("La orden debe contener al menos un producto").build();
//        }
//
//        Set<Product> managedProducts = products.stream()
//                .map(product -> {
//                    try {
//                        return productDAO.findById(product.getId())
//                                .orElseThrow(() -> NotFoundException.builder()
//                                        .message("No se encuentra el Producto id= " + product.getId())
//                                        .build());
//                    } catch (NotFoundException e) {
//                        throw new RuntimeException(e);
//                    }
//                })
//                .collect(Collectors.toSet());
//
//        // Calcular total (opcional)
//        BigDecimal total = managedProducts.stream()
//                .map(Product::getPrice)
//                .reduce(BigDecimal.ZERO, BigDecimal::add);
//
//        // Crear nueva orden
//        PurchaseOrder newOrder = new PurchaseOrder();
//        newOrder.setUser(userFound.get());
//        newOrder.setProducts(managedProducts);
//        newOrder.setTotal(total);
//
//        // Validar balance del usuario
//        User userEntity = userFound.get();
//        if (total.compareTo(userEntity.getBalance()) > 0) {
//            newOrder.setStatus(PurchaseOrder.OrderStatus.FAILED);
//            newOrder.setDescription("Saldo insuficiente para completar la orden. Saldo actual: "
//                    + userEntity.getBalance() + ", Total requerido: " + total);
//        } else {
//            newOrder.setStatus(PurchaseOrder.OrderStatus.PENDING);
//        }
//
//        try {
//            return purchaseOrderDAO.save(newOrder);
//        } catch (Exception e) {
//            log.error(e.getMessage(), e);
//            throw BusinessException.builder().message("Error al crear la Orden").build();
//        }
//    }
    @Transactional
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
            orderFound.setDescription("Saldo insuficiente para completar la orden. Saldo actual: "
                    + user.getBalance() + ", Total requerido: " + total);
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

    @Transactional
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

}