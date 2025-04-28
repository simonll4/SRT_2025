package ar.edu.srt.model.business.interfaces;


import ar.edu.srt.model.User;
import ar.edu.srt.model.business.exceptions.BusinessException;
import ar.edu.srt.model.business.exceptions.FoundException;
import ar.edu.srt.model.business.exceptions.NotFoundException;

import java.util.List;

public interface IUserBusiness {

    public List<User> list() throws BusinessException;

    public User load(Long id) throws NotFoundException, BusinessException;

    public User load(String externalId) throws NotFoundException, BusinessException;

    public User add(User user) throws FoundException, BusinessException;

    public User update(User user) throws NotFoundException, BusinessException, FoundException;

    //    public void delete(User user) throws NotFoundException, BusinessException;

    public void delete(long id) throws NotFoundException, BusinessException;

}
