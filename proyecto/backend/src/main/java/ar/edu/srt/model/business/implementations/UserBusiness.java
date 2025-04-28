package ar.edu.srt.model.business.implementations;


import ar.edu.srt.model.User;
import ar.edu.srt.model.business.exceptions.BusinessException;
import ar.edu.srt.model.business.exceptions.FoundException;
import ar.edu.srt.model.business.exceptions.NotFoundException;
import ar.edu.srt.model.business.interfaces.IUserBusiness;
import ar.edu.srt.model.persistence.UserRepository;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.*;

@Service
@Slf4j
public class UserBusiness implements IUserBusiness {

    @Autowired
    private UserRepository userDAO;

    @Override
    public List<User> list() throws BusinessException {
        try {
            return userDAO.findAll();
        } catch (Exception e) {
            log.error(e.getMessage(), e);
            throw BusinessException.builder().ex(e).build();
        }
    }

    @Override
    public User load(Long id) throws NotFoundException, BusinessException {
        Optional<User> userFound;

        try {
            userFound = userDAO.findById(id);
        } catch (Exception e) {
            log.error(e.getMessage(), e);
            throw BusinessException.builder().ex(e).build();
        }
        if (userFound.isEmpty())
            throw NotFoundException.builder().message("No se encuentra el Usuario id= " + id).build();
        return userFound.get();
    }

    @Override
    public User load(String externalId) throws NotFoundException, BusinessException {
        Optional<User> userFound;

        try {
            userFound = userDAO.findByExternalId(externalId);
        } catch (Exception e) {
            log.error(e.getMessage(), e);
            throw BusinessException.builder().ex(e).build();
        }
        if (userFound.isEmpty())
            throw NotFoundException.builder().message("No se encuentra el Usuario con idExternald= " + externalId).build();
        return userFound.get();
    }

    @Override
    public User add(User user) throws FoundException, BusinessException {

        try {
            load(user.getExternalId());
            throw FoundException.builder().message("Se encontro el Usuario con externalId = " + user.getExternalId()).build();
        } catch (NotFoundException ignored) {
        }

        user.setEnabled(true);
        try {
            return userDAO.save(user);
        } catch (Exception e) {
            log.error(e.getMessage(), e);
            throw BusinessException.builder().ex(e).build();
        }
    }


    @Override
    public User update(User user) throws NotFoundException, BusinessException, FoundException {

       // User userToUpdate = load(user.getId());
        Optional<User> userFound;

        try {
            userFound = userDAO.findByExternalIdAndIdNot(user.getExternalId(), user.getId());
        } catch (Exception e) {
            log.error(e.getMessage(), e);
            throw BusinessException.builder().ex(e).build();
        }

        if (userFound.isPresent()) {
            throw FoundException.builder().message("Se encontró el Usuario con externalId: " + user.getExternalId()).build();
        }

        try {
            //user.setPassword(userToUpdate.getPassword());
            return userDAO.save(user);
        } catch (Exception e) {
            log.error(e.getMessage(), e);
            throw BusinessException.builder().ex(e).build();
        }
    }

//    @Override
//    public void delete(User user) throws NotFoundException, BusinessException {
//        delete(user.getId());
//    }

    @Override
    public void delete(long id) throws NotFoundException, BusinessException {
        load(id);

        try {
            userDAO.deleteById(id);
        } catch (Exception e) {
            log.error(e.getMessage(), e);
            throw BusinessException.builder().ex(e).build();
        }
    }

}