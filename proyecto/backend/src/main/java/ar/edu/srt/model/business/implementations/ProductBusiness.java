package ar.edu.srt.model.business.implementations;

import java.util.List;
import java.util.Optional;

import ar.edu.srt.model.business.exceptions.BusinessException;
import ar.edu.srt.model.business.exceptions.FoundException;
import ar.edu.srt.model.business.exceptions.NotFoundException;
import ar.edu.srt.model.business.interfaces.IProductBusiness;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import ar.edu.srt.model.Product;
import ar.edu.srt.model.persistence.ProductRepository;
import lombok.extern.slf4j.Slf4j;

@Service
@Slf4j
public class ProductBusiness implements IProductBusiness {

    @Autowired
    private ProductRepository productDAO;

    @Override
    public Product load(long id) throws NotFoundException, BusinessException {
        Optional<Product> productFound;

        try {
            productFound = productDAO.findById(id);
        } catch (Exception e) {
            log.error(e.getMessage(), e);
            throw BusinessException.builder().ex(e).build();
        }
        if (productFound.isEmpty())
            throw NotFoundException.builder().message("No se encuentra el Producto id= " + id).build();
        return productFound.get();
    }

    @Override
    public Product load(String product) throws NotFoundException, BusinessException {
        Optional<Product> productFound;

        try {
            productFound = productDAO.findByProduct(product);
        } catch (Exception e) {
            log.error(e.getMessage(), e);
            throw BusinessException.builder().ex(e).build();
        }
        if (productFound.isEmpty())
            throw NotFoundException.builder().message("No se Encuentra el Producto Denominado " + product).build();
        return productFound.get();
    }


    @Override
    public Product add(Product product) throws FoundException, BusinessException {

        try {
            load(product.getProduct());
            throw FoundException.builder().message("Ya existe el Producto " + product.getProduct()).build();
        } catch (NotFoundException e) {
            // log.trace(e.getMessage(), e);
        }

        try {
            return productDAO.save(product);
        } catch (Exception e) {
            log.error(e.getMessage(), e);
            throw BusinessException.builder().message("Error al Crear Nuevo Producto").build();
        }

    }

    @Override
    public List<Product> list() throws BusinessException {
        try {
            return productDAO.findAll();
        } catch (Exception e) {
            log.error(e.getMessage(), e);
            throw BusinessException.builder().ex(e).build();
        }
    }

    @Override
    public Product update(Product product) throws NotFoundException, FoundException, BusinessException {

        Product existingProduct = load(product.getId());
        // Actualizar solo los campos necesarios
        existingProduct.setProduct(product.getProduct());
        existingProduct.setPrice(product.getPrice());

        Optional<Product> productFound;
        try {
            productFound = productDAO.findByProductAndIdNot(product.getProduct(), product.getId());
        } catch (Exception e) {
            log.error(e.getMessage(), e);
            throw BusinessException.builder().ex(e).build();
        }

        if (productFound.isPresent()) {
            throw FoundException.builder().message("Ya Existe un Producto con el Nombre =" + product.getProduct()).build();
        }

        try {
            return productDAO.save(existingProduct);
        } catch (Exception e) {
            log.error(e.getMessage(), e);
            //throw BusinessException.builder().ex(e).build();
            throw BusinessException.builder().message("Error al Actualizar Producto").build();
        }
    }

    @Override
    public void delete(Product product) throws NotFoundException, BusinessException {
        delete(product.getId());
    }

    @Override
    public void delete(long id) throws NotFoundException, BusinessException {
        load(id);
        try {
            productDAO.deleteById(id);
        } catch (Exception e) {
            log.error(e.getMessage(), e);
            throw BusinessException.builder().ex(e).build();
        }

    }

}