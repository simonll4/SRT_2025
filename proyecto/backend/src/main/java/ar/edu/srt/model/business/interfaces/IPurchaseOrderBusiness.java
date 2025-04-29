package ar.edu.srt.model.business.interfaces;

import ar.edu.srt.model.OrderItem;
import ar.edu.srt.model.PurchaseOrder;
import ar.edu.srt.model.business.exceptions.BusinessException;
import ar.edu.srt.model.business.exceptions.FoundException;
import ar.edu.srt.model.business.exceptions.NotFoundException;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

public interface IPurchaseOrderBusiness {

    PurchaseOrder load(Long id) throws NotFoundException, BusinessException;

    PurchaseOrder add(PurchaseOrder purchaseOrder) throws FoundException, BusinessException, NotFoundException;

    List<PurchaseOrder> list() throws BusinessException;

    PurchaseOrder completeOrder(PurchaseOrder order) throws NotFoundException, BusinessException, FoundException;

    PurchaseOrder cancelOrder(PurchaseOrder order) throws NotFoundException, BusinessException;


    @Transactional
    PurchaseOrder updateOrderItems( List<OrderItem> itemsToUpdate)
            throws NotFoundException, BusinessException;
}