package ar.edu.srt.model.business.interfaces;

import java.util.List;

import ar.edu.srt.model.Product;
import ar.edu.srt.model.business.exceptions.BusinessException;
import ar.edu.srt.model.business.exceptions.FoundException;
import ar.edu.srt.model.business.exceptions.NotFoundException;

public interface IProductBusiness {

    public List<Product> list() throws BusinessException;

    public Product load(long id) throws NotFoundException, BusinessException;

    public Product load(String product) throws NotFoundException, BusinessException;

    public Product add(Product product) throws FoundException, BusinessException;

    public Product update(Product product) throws NotFoundException, BusinessException, FoundException;

    public void delete(Product product) throws NotFoundException, BusinessException;

    public void delete(long id) throws NotFoundException, BusinessException;

}