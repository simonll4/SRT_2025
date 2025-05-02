package ar.edu.srt.model.persistence;


import ar.edu.srt.model.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface UserRepository extends JpaRepository<User, Long> {
    Optional<User> findByExternalId(String exteralId);

    Optional<User> findByExternalIdAndIdNot(String externalId, Long id);
}
